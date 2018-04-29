# coding: utf-8
from __future__ import unicode_literals

from uuid import uuid4
import re

from .common import InfoExtractor
from ..utils import (
    compat_str,
    ExtractorError,
    sanitized_Request,
    urlencode_postdata,
)


class ZattooBaseIE(InfoExtractor):

    _NETRC_MACHINE = 'zattoo'
    _HOST_URL = 'https://zattoo.com'

    _power_guide_hash = None

    def _login(self, uuid, session_id):
        (username, password) = self._get_login_info()
        if not username or not password:
            raise ExtractorError(
                'A valid %s account is needed to access this media.' % self._NETRC_MACHINE,
                expected=True)
        login_form = {
            'login': username,
            'password': password,
            'remember': True,
        }
        request = sanitized_Request(
            '%s/zapi/v2/account/login' % self._HOST_URL,
            urlencode_postdata(login_form))
        request.add_header(
            'Referer', '%s/login' % self._HOST_URL)
        request.add_header(
            'Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        request.add_header(
            'Cookie', 'uuid=%s; beaker.session.id=%s' % (uuid, session_id))
        response = self._request_webpage(
            request, None, 'Logging in')
        data = self._parse_json(response.read(), None)
        return data['session']['power_guide_hash']

    def _get_app_token_and_version(self):
        host_webpage = self._download_webpage(
            self._HOST_URL, None, 'Downloading %s' % self._HOST_URL)
        app_token = self._html_search_regex(
            r'<script.+window\.appToken\s*=\s*\'(.+)\'', host_webpage, 'app token')
        app_version = self._html_search_regex(
            r'<!--\w+-(.+?)-', host_webpage, 'app version', default='2.8.2')
        return app_token, app_version

    def _say_hello(self, uuid, app_token, app_version):
        postdata = {
            'client_app_token': app_token,
            'uuid': uuid,
            'lang': 'en',
            'app_version': app_version,
            'format': 'json',
        }
        request = sanitized_Request(
            '%s/zapi/v2/session/hello' % self._HOST_URL,
            urlencode_postdata(postdata))
        response = self._request_webpage(
            request, None, 'Say hello')

        cookie = response.headers.get('Set-Cookie')
        session_id = self._search_regex(
            r'beaker\.session\.id\s*=\s*(.+?);', cookie, 'session id')
        return session_id

    def _extract_cid(self, video_id, channel_name):
        channel_groups = self._download_json(
            '%s/zapi/v2/cached/channels/%s' % (self._HOST_URL,
                                               self._power_guide_hash),
            video_id,
            'Downloading available channel list',
            query={'details': False})['channel_groups']
        channel_list = []
        for chgrp in channel_groups:
            channel_list.extend(chgrp['channels'])
        try:
            return next(
                chan['cid'] for chan in channel_list
                if chan['display_alias'] == channel_name or chan['cid'] == channel_name)
        except StopIteration:
            raise ExtractorError('Could not extract channel id')

    def _extract_cid_and_video_info(self, video_id):
        data = self._download_json(
            '%s/zapi/program/details' % self._HOST_URL,
            video_id,
            'Downloading video information',
            query={
                'program_id': video_id,
                'complete': True
            })

        info_dict = {
            'id': video_id,
            'title': data['program']['title'],
            'description': data['program'].get('description'),
            'thumbnail': data['program'].get('image_url')
        }
        cid = data['program']['cid']
        return cid, info_dict

    def _extract_formats(self, cid, video_id, record_id=None, is_live=False):
        postdata = {
            'stream_type': 'dash',
            'https_watch_urls': True,
        }
        if record_id:
            url = '%s/zapi/watch/recording/%s' % (self._HOST_URL, record_id)
        else:
            url = '%s/zapi/watch/recall/%s/%s' % (self._HOST_URL, cid, video_id)

        if is_live:
            postdata.update({'timeshift': 10800})
            url = '%s/zapi/watch/live/%s' % (self._HOST_URL, cid)

        data = self._download_json(
            sanitized_Request(url, urlencode_postdata(postdata)),
            video_id, 'Downloading dash formats')

        formats = []
        for elem in data['stream']['watch_urls']:
            audio_channel = elem.get('audio_channel')
            maxrate = elem.get('maxrate')
            formats.extend(
                self._extract_mpd_formats(
                    elem['url'], video_id,
                    mpd_id='dash-maxrate-%s-channel-%s' % (maxrate, audio_channel), fatal=False))

        postdata.update({'stream_type': 'hls'})
        request = sanitized_Request(
            url, urlencode_postdata(postdata))
        data = self._download_json(
            request, video_id, 'Downloading hls formats')
        for elem in data['stream']['watch_urls']:
            audio_channel = elem.get('audio_channel')
            preference = None

            # Prefer audio channel A:
            if audio_channel == 'A':
                preference = 1

            maxrate = elem.get('maxrate')
            formats.extend(
                self._extract_m3u8_formats(
                    elem['url'], video_id, 'mp4', entry_protocol='m3u8_native',
                    preference=preference,
                    m3u8_id='hls-maxrate-%s-channel-%s' % (maxrate, audio_channel),
                    fatal=False))

        self._sort_formats(formats)
        return formats

    def _real_initialize(self):
        uuid = compat_str(uuid4())
        app_token, app_version = self._get_app_token_and_version()
        session_id = self._say_hello(uuid, app_token, app_version)
        self._power_guide_hash = self._login(uuid, session_id)

    def _extract_video(self, channel_name, video_id, record_id=None, is_live=False):
        if is_live:
            cid = self._extract_cid(video_id, channel_name)
            info_dict = {
                'id': channel_name,
                'title': self._live_title(channel_name),
                'is_live': True,
            }
        else:
            cid, info_dict = self._extract_cid_and_video_info(video_id)
        formats = self._extract_formats(
            cid, video_id, record_id=record_id, is_live=is_live)
        info_dict['formats'] = formats
        return info_dict


class QuicklineBaseIE(ZattooBaseIE):
    _NETRC_MACHINE = 'quickline'
    _HOST_URL = 'https://mobiltv.quickline.com'


class QuicklineIE(QuicklineBaseIE):
    _VALID_URL = r'https?://(?:www\.)?mobiltv\.quickline\.com/watch/(?P<channel>[^/]+)/(?P<id>[0-9]+)'

    def _real_extract(self, url):
        channel_name, video_id = re.match(self._VALID_URL, url).groups()
        return self._extract_video(channel_name, video_id)


class QuicklineLiveIE(QuicklineBaseIE):
    _VALID_URL = r'https?://(?:www\.)?mobiltv\.quickline\.com/watch/(?P<id>[^/]+)$'

    def _real_extract(self, url):
        channel_name = video_id = self._match_id(url)
        return self._extract_video(channel_name, video_id, is_live=True)


class ZattooIE(ZattooBaseIE):
    _VALID_URL = r'https?://(?:www\.)?zattoo\.com/watch/(?P<channel>[^/]+?)/(?P<id>[0-9]+)[^/]+(?:/(?P<recid>[0-9]+))?'

    # Since regular videos are only available for 7 days and recorded videos
    # are only available for a specific user, we cannot have detailed tests.
    _TESTS = [{
        'url': 'https://zattoo.com/watch/prosieben/130671867-maze-runner-die-auserwaehlten-in-der-brandwueste',
        'only_matching': True,
    }, {
        'url': 'https://zattoo.com/watch/srf_zwei/132905652-eishockey-spengler-cup/102791477/1512211800000/1514433500000/92000',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        channel_name, video_id, record_id = re.match(self._VALID_URL, url).groups()
        return self._extract_video(channel_name, video_id, record_id)


class ZattooLiveIE(ZattooBaseIE):
    _VALID_URL = r'https?://(?:www\.)?zattoo\.com/watch/(?P<id>[^/]+)$'

    _TEST = {
        'url': 'https://zattoo.com/watch/srf1',
        'only_matching': True,
    }

    def _real_extract(self, url):
        channel_name = video_id = self._match_id(url)
        return self._extract_video(channel_name, video_id, is_live=True)
