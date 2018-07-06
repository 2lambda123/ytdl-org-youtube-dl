# coding: utf-8
from __future__ import unicode_literals

import collections
import re

from .common import InfoExtractor
from ..compat import (
    compat_urlparse)
from ..utils import (
    ExtractorError,
    urlencode_postdata,
    qualities, unescapeHTML)


class FrontEndMasterBaseIE(InfoExtractor):
    _API_BASE = 'https://api.frontendmasters.com/v1/kabuki/courses'
    _VIDEO_BASE = 'http://www.frontendmasters.com/courses'
    _CAPTIONS_BASE = 'https://api.frontendmasters.com/v1/kabuki/transcripts'
    _COOKIES_BASE = 'https://api.frontendmasters.com'
    _LOGIN_URL = 'https://frontendmasters.com/login/'

    _QUALITIES_PREFERENCE = ('low', 'medium', 'high')
    _QUALITIES = {
        'low': {'width': 480, 'height': 360},
        'medium': {'width': 1280, 'height': 720},
        'high': {'width': 1920, 'height': 1080}
    }

    AllowedQuality = collections.namedtuple('AllowedQuality',
                                            ['ext', 'qualities'])
    _ALLOWED_QUALITIES = [
        AllowedQuality('webm', ['low', 'medium', 'high']),
        AllowedQuality('mp4', ['low', 'medium', 'high'])
    ]

    def _real_initialize(self):
        self._login()

    def _login(self):
        (username, password) = self._get_login_info()
        if username is None:
            return

        login_page = self._download_webpage(
            self._LOGIN_URL, None, 'Downloading login page')

        login_form = self._hidden_inputs(login_page)

        login_form.update({
            'username': username,
            'password': password
        })

        post_url = self._search_regex(
            r'<form[^>]+action=(["\'])(?P<url>.+?)\1', login_page,
            'post_url', default=self._LOGIN_URL, group='url')

        if not post_url.startswith('http'):
            post_url = compat_urlparse.urljoin(self._LOGIN_URL, post_url)

        response = self._download_webpage(
            post_url, None, 'Logging in',
            data=urlencode_postdata(login_form),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        error = self._search_regex(
            r'<div[^>]+class=["\']Message MessageAlert["\'][^>]*>'
            r'([^<]+)'
            r'</div>',
            response, 'error message', default=None)

        if error:
            raise ExtractorError('Unable to login: %s' % unescapeHTML(error),
                                 expected=True)

    def _download_course(self, course_id, url):
        response = self._download_json(
            '%s/%s' % (self._API_BASE, course_id), course_id,
            'Downloading course JSON',
            headers={
                'Content-Type': 'application/json;charset=utf-8',
                'Referer': url,
            })
        return response

    @staticmethod
    def _pair_section_video_element(lesson_elements):
        sections = {}
        current_section = None
        current_section_number = 0
        for elem in lesson_elements:
            if not isinstance(elem, int):
                elem_name = elem
                if not isinstance(elem_name, str):
                    # convert unicode to str
                    elem_name = elem.encode('utf-8')
                (current_section, current_section_number) = \
                    (elem_name, current_section_number + 1)
            else:
                if current_section:
                    sections[elem] = (current_section, current_section_number)

        return sections


class FrontEndMasterIE(FrontEndMasterBaseIE):
    IE_NAME = 'frontend-masters'
    _VALID_URL = r'https?://(?:www\.)?frontendmasters\.com/courses/' \
                 r'(?P<courseid>[a-z\-]+)/' \
                 r'(?P<id>[a-z\-]+)'

    _NETRC_MACHINE = 'frontendmasters'

    _TEST = {
        'url': 'https://frontendmasters.com/courses/web-development/tools',
        'md5': '7f161159710d6b7016a4f4af6fcb05e2',
        'info_dict': {
            'id': 'tools',
            'title': 'Tools',
            'display_id': 'tools',
            'description': 'md5:82c1ea6472e88ed5acd1829fe992e4f7',
            'ext': 'mp4'
        },
        'skip': 'Requires FrontendMasters account credentials',
    }

    def _get_subtitles(self, video_hash, video_id):
        captions = self._download_webpage(
            '%s/%s.vtt' % (self._CAPTIONS_BASE, video_hash), video_id,
            fatal=False)
        if captions:
            return {
                'en': [{
                    'ext': 'vtt',
                    'data': captions
                }]
            }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        course_id = mobj.group('courseid')

        course_json_content = self._download_course(course_id=course_id,
                                                    url=url)

        # Necessary to get mandatory informations like title and video_url
        lesson_index = course_json_content.get('lessonSlugs').index(video_id)
        lesson_hash = course_json_content.get('lessonHashes')[lesson_index]
        lesson_data = course_json_content.get('lessonData')[lesson_hash]
        # This is necessary to get the link for the video
        lesson_source_base = lesson_data['sourceBase']

        lesson_title = lesson_data['title']

        # Some optional fields
        lesson_description = lesson_data.get('description')
        lesson_index = lesson_data.get('index')
        lesson_slug = lesson_data.get('slug')
        lesson_thumbnail_url = lesson_data.get('thumbnail')
        lesson_section_elements = course_json_content.get('lessonElements')

        try:
            course_sections_pairing = self._pair_section_video_element(
                lesson_section_elements)

            lesson_section = \
                course_sections_pairing.get(lesson_index)[0]

            lesson_section_number = \
                course_sections_pairing.get(lesson_index)[1]
        except Exception:
            lesson_section = None
            lesson_section_number = None

        video_request_url = '%s/source'
        video_request_headers = {
            'origin': 'https://frontendmasters.com',
            'referer': lesson_source_base,
        }

        quality_key = qualities(self._QUALITIES_PREFERENCE)

        formats = []
        for ext, qualities_ in self._ALLOWED_QUALITIES:
            for quality in qualities_:
                f = self._QUALITIES[quality].copy()
                video_request_params = {
                    'r': f['height'],
                    'f': ext
                }
                video_response = self._download_json(
                    video_request_url % lesson_source_base, video_id,
                    query=video_request_params, headers=video_request_headers)

                video_url = video_response.get('url')
                clip_f = f.copy()
                clip_f.update({
                    'url': video_url,
                    'ext': ext,
                    'format_id': '%s-%s' % (ext, quality),
                    'quality': quality_key(quality),
                    'height': f['height']
                })
                formats.append(clip_f)

        self._sort_formats(formats)

        subtitles = self.extract_subtitles(lesson_hash, video_id)

        return {
            'id': video_id,
            'display_id': lesson_slug,
            'title': lesson_title,
            'description': lesson_description,
            'chapter': lesson_section,
            'chapter_number': lesson_section_number,
            'thumbnail': lesson_thumbnail_url,
            'formats': formats,
            'subtitles': subtitles
        }


class FrontEndMasterCourseIE(FrontEndMasterBaseIE):
    IE_NAME = 'frontend-masters:course'
    _VALID_URL = r'https?://(?:www\.)?frontendmasters\.com/courses/(?P<courseid>[a-z\-]+)/?$'

    _NETRC_MACHINE = 'frontendmasters'

    _TEST = {
        'url': 'https://frontendmasters.com/courses/javascript-basics/',
        'info_dict': {
            'id': 'javascript-basics',
            'title': 'Introduction to JavaScript Programming',
            'description': 'md5:269412fbb76d86954761599ad8e4cbc9'
        },
        'playlist_count': 19,
        'skip': 'Requires FrontendMasters account credentials'
    }

    @classmethod
    def suitable(cls, url):
        return False if FrontEndMasterIE.suitable(url) else super(FrontEndMasterBaseIE, cls).suitable(url)

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        course_id = mobj.group('courseid')
        course_json_content = self._download_course(course_id=course_id,
                                                    url=url)

        title = course_json_content.get('title')
        description = course_json_content.get('description')
        course_display_id = course_json_content.get('slug')

        videos_data = course_json_content.get('lessonData').values()
        videos_data = sorted(videos_data, key=lambda video: video.get('index'))

        entries = []
        for video in videos_data:
            video_slug = video.get('slug')
            clip_url = '%s/%s/%s' % (
                self._VIDEO_BASE, course_display_id, video_slug)
            entries.append({
                '_type': 'url_transparent',
                'url': clip_url,
                'ie_key': FrontEndMasterIE.ie_key()
            })

        return self.playlist_result(entries, course_id, title, description)
