# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import (
    compat_str,
)
from ..utils import (
    clean_html,
    ExtractorError,
    get_element_by_class,
    int_or_none,
    str_or_none,
    strip_or_none,
    try_get,
    urlencode_postdata,
    urljoin,
)


class PlatziBaseIE(InfoExtractor):
    _LOGIN_URL = 'https://platzi.com/login/'
    _NETRC_MACHINE = 'platzi'

    def _real_initialize(self):
        self._login()

    def _login(self):
        username, password = self._get_login_info()
        if username is None:
            return

        login_page = self._download_webpage(
            self._LOGIN_URL, None, 'Downloading login page')

        login_form = self._hidden_inputs(login_page)

        login_form.update({
            'email': username,
            'password': password,
        })

        urlh = self._request_webpage(
            self._LOGIN_URL, None, 'Logging in',
            data=urlencode_postdata(login_form),
            headers={'Referer': self._LOGIN_URL})

        # login succeeded
        if 'platzi.com/login' not in urlh.geturl():
            return

        login_error = self._webpage_read_content(
            urlh, self._LOGIN_URL, None, 'Downloading login error page')

        login = self._parse_json(
            self._search_regex(
                r'login\s*=\s*({.+?})(?:\s*;|\s*</script)', login_error, 'login'),
            None)

        for kind in ('error', 'password', 'nonFields'):
            error = str_or_none(login.get('%sError' % kind))
            if error:
                raise ExtractorError(
                    'Unable to login: %s' % error, expected=True)
        raise ExtractorError('Unable to log in')


class PlatziIE(PlatziBaseIE):
    _VALID_URL = r'''(?x)
                    https?://
                        (?:
                            platzi\.com/clases|           # es version
                            courses\.platzi\.com/classes  # en version
                        )/[^/]+/(?P<id>\d+)-[^/?\#&]+
                    '''

    _TESTS = [{
        'url': 'https://platzi.com/clases/1311-next-js/12074-creando-nuestra-primera-pagina/',
        'md5': '8f56448241005b561c10f11a595b37e3',
        'info_dict': {
            'id': '12074',
            'ext': 'mp4',
            'title': 'Creando nuestra primera página',
            'description': 'md5:4c866e45034fc76412fbf6e60ae008bc',
            'duration': 420,
        },
        'skip': 'Requires platzi account credentials',
    }, {
        'url': 'https://courses.platzi.com/classes/1367-communication-codestream/13430-background/',
        'info_dict': {
            'id': '13430',
            'ext': 'mp4',
            'title': 'Background',
            'description': 'md5:49c83c09404b15e6e71defaf87f6b305',
            'duration': 360,
        },
        'skip': 'Requires platzi account credentials',
        'params': {
            'skip_download': True,
        },
    }]

    def _real_extract(self, url):
        lecture_id = self._match_id(url)

        headers = {'User-Agent': 'Mozilla/5.0'}
        webpage = self._download_webpage(url, lecture_id, headers=headers)
        data_preloaded_state = self._parse_json(
            self._search_regex(
                (r'window\s*.\s*__PRELOADED_STATE__\s*=\s*({.*?});?\s*</script'), webpage, 'client data'),
            lecture_id)

        video_player = try_get(data_preloaded_state, lambda x: x['videoPlayer'], dict)
        title = strip_or_none(video_player.get('name')) or self._og_search_title(webpage)
        servers = try_get(video_player, lambda x: x['video']['servers'], dict) or {}
        formats = []
        headers['Referer'] = url
        extractions = {
            'hls': lambda x: formats.extend(self._extract_m3u8_formats(
                        server_json[x], lecture_id, 'mp4',
                        entry_protocol='m3u8_native', m3u8_id='hls',
                        note='Downloading %s m3u8 information' % (server_json.get('id', x), ),
                        headers=headers, fatal=False)),
            'dash': lambda x: formats.extend(self._extract_mpd_formats(
                        server_json[x], lecture_id, mpd_id='dash',
                        note='Downloading %s MPD manifest' % (server_json.get('id', x), ),
                        headers=headers, fatal=False)),
        }
        for server, server_json in servers.items():
            if not isinstance(server_json, dict):
                continue
            for fmt in server_json.keys():
                extraction = extractions.get(fmt)
                if callable(extraction):
                    extraction(fmt)
        self._sort_formats(formats)
        for f in formats:
            f.setdefault('http_headers', {})['Referer'] = headers['Referer']

        return {
            'id': lecture_id,
            'title': title,
            'description': self._og_search_description(webpage),
            'thumbnail': self._og_search_thumbnail(webpage),
            'duration': int_or_none(video_player.get('duration'), invscale=60),
            'creator': clean_html(get_element_by_class('TeacherDetails-name', webpage)),
            'formats': formats,
        }


class PlatziCourseIE(PlatziBaseIE):
    _VALID_URL = r'''(?x)
                    https?://
                        (?:
                            platzi\.com/clases|           # es version
                            courses\.platzi\.com/classes  # en version
                        )/(?P<id>[^/?\#&]+)
                    '''
    _TESTS = [{
        'url': 'https://platzi.com/clases/next-js/',
        'info_dict': {
            'id': '1311',
            'title': 'Curso de Next.js',
        },
        'playlist_count': 22,
    }, {
        'url': 'https://courses.platzi.com/classes/communication-codestream/',
        'info_dict': {
            'id': '1367',
            'title': 'Codestream Course',
        },
        'playlist_count': 14,
    }]

    @classmethod
    def suitable(cls, url):
        return False if PlatziIE.suitable(url) else super(PlatziCourseIE, cls).suitable(url)

    def _real_extract(self, url):
        course_name = self._match_id(url)

        webpage = self._download_webpage(url, course_name)

        initialData = self._search_regex(
            (r'window.initialData\s*=\s*({.+?})\s*;\s*\n', r'window.initialData\s*=\s*({.+?})\s*;'),
            webpage, 'initialData')
        props = self._parse_json(initialData, course_name, default={})
        props = try_get(props, lambda x: x['initialProps'], dict) or {}
        entries = []
        for chapter_num, chapter in enumerate(props.get('concepts') or [], 1):
            if not isinstance(chapter, dict):
                continue
            materials = chapter.get('materials')
            if not materials or not isinstance(materials, list):
                continue
            chapter_title = chapter.get('title')
            chapter_id = str_or_none(chapter.get('id'))
            for material in materials:
                if not isinstance(material, dict):
                    continue
                if material.get('material_type') != 'video':
                    continue
                video_url = urljoin(url, material.get('url'))
                if not video_url:
                    continue
                entries.append({
                    '_type': 'url_transparent',
                    'url': video_url,
                    'title': str_or_none(material.get('name')),
                    'id': str_or_none(material.get('id')),
                    'ie_key': PlatziIE.ie_key(),
                    'chapter': chapter_title,
                    'chapter_number': chapter_num,
                    'chapter_id': chapter_id,
                })

        course_id = compat_str(try_get(props, lambda x: x['course']['id']))
        course_title = try_get(props, lambda x: x['course']['name'], compat_str)

        result = self.playlist_result(entries, course_id, course_title)
        desc = clean_html(get_element_by_class('RouteDescription-content', webpage))
        if desc:
            result['description'] = desc
        return result
