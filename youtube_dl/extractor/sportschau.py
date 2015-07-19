# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor


class SportschauIE(InfoExtractor):
    IE_NAME = 'Sportschau'
    _VALID_URL = r'https?://(?:www\.)?sportschau\.de/\w+(?:/\w+)?/video(?P<id>\w+)\.html'
    _TEST = {
        'url': 'http://www.sportschau.de/tourdefrance/videoseppeltkokainhatnichtsmitklassischemdopingzutun100.html',
        'md5': 'a6ef460ab9f4089b079832e06d554cec',
        'info_dict': {
            'id': 'seppeltkokainhatnichtsmitklassischemdopingzutun100',
            'ext': 'mp4',
            'title': 'Seppelt: "Kokain hat nichts mit klassischem Doping zu tun" - Tour de France - sportschau.de',
            'thumbnail': 're:^https?://.*\.jpg$',
            'description': 'Der ARD-Doping Experte Hajo Seppelt gibt seine Einschätzung zum ersten Dopingfall der diesjährigen Tour de France um den Italiener Luca Paolini ab.',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        ext = '-mc_defaultQuality-h.json'
        json_url = url[:-5] + ext

        json = self._download_json(json_url, video_id)
        thumb_url = json['_previewImage']

        m3u8_url = json['_mediaArray'][1]['_mediaStreamArray'][0]['_stream'][0]
        m3u8_formats = self._extract_m3u8_formats(m3u8_url, video_id, ext="mp4")

        webpage = self._download_webpage(url, video_id)
        title = self._html_search_regex(r'<title>(.*?)</title>', webpage, 'title')
        desc = self._html_search_meta('description', webpage)

        return {
            'id': video_id,
            'title': title,
            'formats': m3u8_formats,
            'description': desc,
            'thumbnail': thumb_url,
        }
