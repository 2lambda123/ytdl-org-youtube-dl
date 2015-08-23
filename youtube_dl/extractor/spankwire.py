from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import (
    compat_urllib_parse_unquote,
    compat_urllib_parse_urlparse,
    compat_urllib_request,
)
from ..utils import (
    str_to_int,
    unified_strdate,
)
from ..aes import aes_decrypt_text


class SpankwireIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?P<url>spankwire\.com/[^/]*/video(?P<videoid>[0-9]+)/?)'
    _TESTS = [{
                'url': 'http://www.spankwire.com/Buckcherry-s-X-Rated-Music-Video-Crazy-Bitch/video103545/',
                'md5': '8bbfde12b101204b39e4b9fe7eb67095',
                    'info_dict': {
                                    'id': '103545',
                                    'ext': 'mp4',
                                    'title': 'Buckcherry`s X Rated Music Video Crazy Bitch',
                                    'description': 'Crazy Bitch X rated music video.',
                                    'uploader': 'oreusz',
                                    'uploader_id': '124697',
                                    'upload_date': '20070507',
                                    'age_limit': 18,
                    }
              },
              {
                'url': 'http://www.spankwire.com/Titcums-Compiloation-I/video1921551/',
                'md5': '09b3c20833308b736ae8902db2f8d7e6',
                    'info_dict': {
                                    'id': '1921551',
                                    'ext': 'mp4',
                                    'title': 'Titcums Compiloation I',
                                    'description': 'cum on tits',
                                    'uploader': 'dannyh78999',
                                    'uploader_id': '3056053',
                                    'upload_date': '20150822',
                                    'age_limit': 18,
                    }
              }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('videoid')
        url = 'http://www.' + mobj.group('url')

        req = compat_urllib_request.Request(url)
        req.add_header('Cookie', 'age_verified=1')
        webpage = self._download_webpage(req, video_id)

        title = self._html_search_regex(
            r'<h1>([^<]+)', webpage, 'title')
        description = self._html_search_regex(
            r'(?s)<div\s+id="descriptionContent">(.+?)</div>',
            webpage, 'description', fatal=False)
        thumbnail = self._html_search_regex(
            r'playerData\.screenShot\s*=\s*["\']([^"\']+)["\']',
            webpage, 'thumbnail', fatal=False)

        uploader = self._html_search_regex(
            r'by:\s*<a [^>]*>(.+?)</a>',
            webpage, 'uploader', fatal=False)
        uploader_id = self._html_search_regex(
            r'by:\s*<a href="/user/viewProfile\?.*?UserId=(\d+).*?"',
            webpage, 'uploader id', fatal=False)
        upload_date = unified_strdate(self._html_search_regex(
            r'</a> on (.+?) at \d+:\d+',
            webpage, 'upload date', fatal=False))

        view_count = str_to_int(self._html_search_regex(
            r'<div id="viewsCounter"><span>([\d,\.]+)</span> views</div>',
            webpage, 'view count', fatal=False))
        comment_count = str_to_int(self._html_search_regex(
            r'<span\s+id="spCommentCount"[^>]*>([\d,\.]+)</span>',
            webpage, 'comment count', fatal=False))

        video_urls = list(map(
            compat_urllib_parse_unquote,
            re.findall(r'playerData\.cdnPath[0-9]{3,}\s*=\s*(?:encodeURIComponent\()?["\']([^"\']+)["\']', webpage)))
        if webpage.find('flashvars\.encrypted = "true"') != -1:
            password = self._search_regex(
                r'flashvars\.video_title = "([^"]+)',
                webpage, 'password').replace('+', ' ')
            video_urls = list(map(
                lambda s: aes_decrypt_text(s, password, 32).decode('utf-8'),
                video_urls))

        formats = []
        for video_url in video_urls:
            path = compat_urllib_parse_urlparse(video_url).path
            format = path.split('/')[4].split('_')[:2]
            if format[0] == 'mp4':
                format_id, quality = format
                format = "-".join(format)
                if quality == 'normal':
                    height = 180
                elif quality == 'high':
                    height = 240
                elif quality == 'ultra':
                    height = 480
                elif quality == '720p':
                    height = 720
                formats.append({
                    'url': video_url,
                    'format': format,
                    'height': height,
                    'format_id': format,
                })
            else:
                resolution, bitrate_str = format
                format = "-".join(format)
                height = int(resolution.rstrip('Pp'))
                tbr = int(bitrate_str.rstrip('Kk'))
                formats.append({
                    'url': video_url,
                    'resolution': resolution,
                    'format': format,
                    'tbr': tbr,
                    'height': height,
                    'format_id': format,
                })
        self._sort_formats(formats)

        age_limit = self._rta_search(webpage)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'uploader': uploader,
            'uploader_id': uploader_id,
            'upload_date': upload_date,
            'view_count': view_count,
            'comment_count': comment_count,
            'formats': formats,
            'age_limit': age_limit,
        }
