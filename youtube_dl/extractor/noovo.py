# coding: utf-8
from __future__ import unicode_literals
from .common import InfoExtractor


class NoovoIE(InfoExtractor):
    IE_NAME = 'Noovo'
    IE_DESC = 'VTele, Max, MusiquePlus'
    _VALID_URL = r'https?://(?:[a-z0-9-]+\.)?noovo\.ca/videos/(?P<id>[a-z0-9-]+/[a-z0-9-]+)'
    _TESTS = [{
        'url': 'http://noovo.ca/videos/rpm-plus/chrysler-imperial',
        'md5': '2fcc04d0a8f4a853fad91233c2fdd121',
        'info_dict': {
            'id': '5386045029001',
            'description': 'Antoine présente des véhicules qu\'il aperçoit sur la rue.',
            'ext': 'mp4',
            'timestamp': 1491399228,
            'title': 'Chrysler Imperial',
            'upload_date': '20170405',
            'uploader_id': '618566855001'
        }
    }, {
        'url': 'http://noovo.ca/videos/l-amour-est-dans-le-pre/episode-13-8',
        'md5': '1199e96fbb93f2d42717115f72097b6b',
        'info_dict': {
            'id': '5395865725001',
            'description': 'md5:336d5ebc5436534e61d16e63ddfca327',
            'ext': 'mp4',
            'timestamp': 1492019320,
            'title': 'md5:2895fdc124639be0ef64ea0d06f5e493',
            'upload_date': '20170412',
            'uploader_id': '618566855001'
        }
    }, {
        'url': 'http://interventions.noovo.ca/911/video/intoxication-aux-drogues-dures/?autoplay=1',
        'only_matching': True
    }]
    API_URL_TEMPLATE = 'http://api.noovo.ca/api/v1/pages/single-episode/%s'
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/618566855001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        api_url = self.API_URL_TEMPLATE % video_id
        api_content = self._download_json(api_url, video_id)

        brightcove_id = api_content.get('data').get('brightcoveId')
        if not brightcove_id:
            brightcove_id = api_content.get('data').get('contents')[0].get('brightcoveId')

        return self.url_result(
            self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id, 'BrightcoveNew', brightcove_id
        )
