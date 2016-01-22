from __future__ import unicode_literals

from .nuevo import NuevoBaseIE


class TruTubeIE(NuevoBaseIE):
    _VALID_URL = r'https?://(?:www\.)?trutube\.tv/(?:video/|nuevo/player/embed\.php\?v=)(?P<id>[0-9]+)'
    _TESTS = [{
        'url': 'http://trutube.tv/video/14880/Ramses-II-Proven-To-Be-A-Red-Headed-Caucasoid-',
        'md5': 'c5b6e301b0a2040b074746cbeaa26ca1',
        'info_dict': {
            'id': '14880',
            'ext': 'flv',
            'title': 'Ramses II - Proven To Be A Red Headed Caucasoid',
            'thumbnail': 're:^http:.*\.jpg$',
        }
    }, {
        'url': 'https://trutube.tv/nuevo/player/embed.php?v=14880',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        config_url = 'https://trutube.tv/nuevo/player/config.php?v=%s' % video_id

        info = self._extract_nuevo(config_url, video_id)

        # filehd always 404s
        info['formats'] = info['formats'][:1]

        return info
