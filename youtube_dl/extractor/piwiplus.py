# encoding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    unified_strdate,
    url_basename,
)


class PiwiplusIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.piwiplus\.fr/.*?/(?P<path>.*)|player\.piwiplus\.fr/#/(?P<id>[0-9]+))'
    _VIDEO_INFO_TEMPLATE = 'http://service.canal-plus.com/video/rest/getVideosLiees/teletoon/%s'
    IE_NAME = 'piwiplus.fr'

    _TEST = {
        'url': 'http://www.piwiplus.fr/videos-piwi/pid1405-le-labyrinthe-boing-super-ranger.html?vid=1108190',
        'md5': '0f55da10e76cab297760f355401897c5',
        'info_dict': {
            'id': '922470',
            'ext': 'flv',
            'title': 'Le labyrinthe - Boing super ranger',
            'upload_date': '20140724',
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.groupdict().get('id')

        # Beware, some subclasses do not define an id group
        display_id = url_basename(mobj.group('path'))

        if video_id is None:
            webpage = self._download_webpage(url, display_id)
            video_id = self._search_regex(r'<canal:player\s[^>]*?videoId="(\d+)"', webpage, 'video id')

        info_url = self._VIDEO_INFO_TEMPLATE % video_id
        doc = self._download_xml(info_url, video_id, 'Downloading video XML')

        video_info = [video for video in doc if video.find('ID').text == video_id][0]
        media = video_info.find('MEDIA')
        infos = video_info.find('INFOS')

        preferences = ['MOBILE', 'BAS_DEBIT', 'HAUT_DEBIT', 'HD', 'HLS', 'HDS']

        formats = [
            {
                'url': fmt.text + '?hdcore=2.11.3' if fmt.tag == 'HDS' else fmt.text,
                'format_id': fmt.tag,
                'ext': 'mp4' if fmt.tag == 'HLS' else 'flv',
                'preference': preferences.index(fmt.tag) if fmt.tag in preferences else -1,
            } for fmt in media.find('VIDEOS') if fmt.text
        ]
        self._sort_formats(formats)

        return {
            'id': video_id,
            'display_id': display_id,
            'title': '%s - %s' % (infos.find('TITRAGE/TITRE').text,
                                  infos.find('TITRAGE/SOUS_TITRE').text),
            'upload_date': unified_strdate(infos.find('PUBLICATION/DATE').text),
            'thumbnail': media.find('IMAGES/GRAND').text,
            'description': infos.find('DESCRIPTION').text,
            'view_count': int(infos.find('NB_VUES').text),
            'like_count': int(infos.find('NB_LIKES').text),
            'comment_count': int(infos.find('NB_COMMENTS').text),
            'formats': formats,
        }