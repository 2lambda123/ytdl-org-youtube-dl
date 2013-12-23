import datetime
import json
import os
import re
import socket

from .common import InfoExtractor
from ..utils import (
    compat_http_client,
    compat_parse_qs,
    compat_str,
    compat_urllib_error,
    compat_urllib_parse_urlparse,
    compat_urllib_request,

    ExtractorError,
    unescapeHTML,
    determine_ext,
)


class BlipTVIE(InfoExtractor):
    """Information extractor for blip.tv"""

    _VALID_URL = r'^(?:https?://)?(?:\w+\.)?blip\.tv/((.+/)|(play/)|(api\.swf#))(.+)$'
    _URL_EXT = r'^.*\.([a-z0-9]+)$'
    IE_NAME = u'blip.tv'
    _TEST = {
        u'url': u'http://blip.tv/cbr/cbr-exclusive-gotham-city-imposters-bats-vs-jokerz-short-3-5796352',
        u'file': u'5779306.m4v',
        u'md5': u'80baf1ec5c3d2019037c1c707d676b9f',
        u'info_dict': {
            u"upload_date": u"20111205", 
            u"description": u"md5:9bc31f227219cde65e47eeec8d2dc596", 
            u"uploader": u"Comic Book Resources - CBR TV", 
            u"title": u"CBR EXCLUSIVE: \"Gotham City Imposters\" Bats VS Jokerz Short 3"
        }
    }
    
    _format_ids = {
        'Source': 'src',
        'Blip LD': 'ld',
        'Blip SD': 'sd',
        'Blip HD 720': 'hd'
    }

    def report_direct_download(self, title):
        """Report information extraction."""
        self.to_screen(u'%s: Direct download detected' % title)

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            raise ExtractorError(u'Invalid URL: %s' % url)

        # See https://github.com/rg3/youtube-dl/issues/857
        embed_mobj = re.search(r'^(?:https?://)?(?:\w+\.)?blip.tv/(?:play/|api\.swf#)([a-zA-Z0-9]+)', url)
        if embed_mobj:
            info_url = 'http://blip.tv/play/%s.x?p=1' % embed_mobj.group(1)
            info_page = self._download_webpage(info_url, None)
            video_id = self._search_regex(r'data-episode-id="(\d+)', info_page, u'video_id')
            return self.url_result('http://blip.tv/a/a-'+video_id, 'BlipTV')

        if '?' in url:
            cchar = '&'
        else:
            cchar = '?'
        json_url = url + cchar + 'skin=json&version=2&no_wrap=1'
        request = compat_urllib_request.Request(json_url)
        request.add_header('User-Agent', 'iTunes/10.6.1')
        self.report_extraction(mobj.group(1))
        info = None
        urlh = self._request_webpage(request, None, False,
            u'unable to download video info webpage')
        if urlh.headers.get('Content-Type', '').startswith('video/'): # Direct download
            basename = url.split('/')[-1]
            title,ext = os.path.splitext(basename)
            ext = ext.replace('.', '')
            self.report_direct_download(title)
            return {
                'id': title,
                'title': title,
                'user_agent': 'iTunes/10.6.1',
                'formats': [{
                    'format_id': 'unk',
                    'url': url,
                    'ext': ext,
                }]
            }

        try:
            json_code_bytes = urlh.read()
            json_code = json_code_bytes.decode('utf-8')
        except (compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error) as err:
            raise ExtractorError(u'Unable to read video info webpage: %s' % compat_str(err))

        try:
            json_data = json.loads(json_code)
            if 'Post' in json_data:
                data = json_data['Post']
            else:
                data = json_data

            upload_date = datetime.datetime.strptime(data['datestamp'], '%m-%d-%y %H:%M%p').strftime('%Y%m%d')
            formats = []
            if 'additionalMedia' in data:
                for raw_format in sorted(data['additionalMedia'], key=lambda f: int(f['media_height'])):
                    if raw_format['media_width'] == '0': # filter m3u8
                        continue
                    formats.append({
                        'url': raw_format['url'],
                        'ext': determine_ext(raw_format['url']),
                        'format_note': raw_format['role'],
                        'format_id': self._format_ids.get(raw_format['role'], raw_format['role']),
                        'width': raw_format['media_width'],
                        'height': raw_format['media_height'],
                    })
            else:
                formats.append({
                    'url': data['media']['url'],
                    'ext': determine_ext(data['media']['url']),
                    'format_id': 'unk',
                    'width': data['media']['width'],
                    'height': data['media']['height'],
                })

            return {
                'id': compat_str(data['item_id']),
                'uploader': data['display_name'],
                'upload_date': upload_date,
                'title': data['title'],
                'thumbnail': data['thumbnailUrl'],
                'description': data['description'],
                'user_agent': 'iTunes/10.6.1',
                'formats': formats 
            }
        except (ValueError,KeyError) as err:
            raise ExtractorError(u'Unable to parse video information: %s' % repr(err))

class BlipTVUserIE(InfoExtractor):
    """Information Extractor for blip.tv users."""

    _VALID_URL = r'(?:(?:(?:https?://)?(?:\w+\.)?blip\.tv/)|bliptvuser:)([^/]+)/*$'
    _PAGE_SIZE = 12
    IE_NAME = u'blip.tv:user'

    def _real_extract(self, url):
        # Extract username
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            raise ExtractorError(u'Invalid URL: %s' % url)

        username = mobj.group(1)

        page_base = 'http://m.blip.tv/pr/show_get_full_episode_list?users_id=%s&lite=0&esi=1'

        page = self._download_webpage(url, username, u'Downloading user page')
        mobj = re.search(r'data-users-id="([^"]+)"', page)
        page_base = page_base % mobj.group(1)


        # Download video ids using BlipTV Ajax calls. Result size per
        # query is limited (currently to 12 videos) so we need to query
        # page by page until there are no video ids - it means we got
        # all of them.

        video_ids = []
        pagenum = 1

        while True:
            url = page_base + "&page=" + str(pagenum)
            page = self._download_webpage(url, username,
                                          u'Downloading video ids from page %d' % pagenum)

            # Extract video identifiers
            ids_in_page = []

            for mobj in re.finditer(r'href="/([^"]+)"', page):
                if mobj.group(1) not in ids_in_page:
                    ids_in_page.append(unescapeHTML(mobj.group(1)))

            video_ids.extend(ids_in_page)

            # A little optimization - if current page is not
            # "full", ie. does not contain PAGE_SIZE video ids then
            # we can assume that this page is the last one - there
            # are no more ids on further pages - no need to query
            # again.

            if len(ids_in_page) < self._PAGE_SIZE:
                break

            pagenum += 1

        urls = [u'http://blip.tv/%s' % video_id for video_id in video_ids]
        url_entries = [self.url_result(vurl, 'BlipTV') for vurl in urls]
        return [self.playlist_result(url_entries, playlist_title = username)]
