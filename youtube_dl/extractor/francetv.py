# coding: utf-8

from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import (
    compat_urlparse,
)
from ..utils import (
    clean_html,
    determine_ext,
    ExtractorError,
    int_or_none,
    try_get,
    url_or_none,
)
from .dailymotion import DailymotionIE


class FranceTVBaseInfoExtractor(InfoExtractor):
    def _make_url_result(self, video_or_full_id, catalog=None):
        full_id = 'francetv:%s' % video_or_full_id
        if '@' not in video_or_full_id and catalog:
            full_id += '@%s' % catalog
        return self.url_result(
            full_id, ie=FranceTVIE.ie_key(),
            video_id=video_or_full_id.split('@')[0])


class FranceTVIE(InfoExtractor):
    _VALID_URL = r'''(?x)
                    (?:
                        https?://
                            sivideo\.webservices\.francetelevisions\.fr/tools/getInfosOeuvre/v2/\?
                            .*?\bidDiffusion=[^&]+|
                        (?:
                            https?://videos\.francetv\.fr/video/|
                            francetv:
                        )
                        (?P<id>[^@]+)(?:@(?P<catalog>.+))?
                    )
                    '''

    _TESTS = [{
        # without catalog
        'url': 'https://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=162311093&callback=_jsonp_loader_callback_request_0',
        'md5': '944fe929c5ed2c05f864085ec5714f98',
        'info_dict': {
            'id': '162311093',
            'ext': 'mp4',
            'title': '13h15, le dimanche... - Les mystères de Jésus',
        },
        'params': {
            'format': 'bestvideo',
        },
        'expected_warnings': 'Unknown MIME type application/mp4 in DASH manifest',
    }, {
        # with catalog
        'url': 'https://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=NI_1004933&catalogue=Zouzous&callback=_jsonp_loader_callback_request_4',
        'only_matching': True,
    }, {
        'url': 'http://videos.francetv.fr/video/NI_657393@Regions',
        'only_matching': True,
    }, {
        'url': 'francetv:162311093',
        'only_matching': True,
    }, {
        'url': 'francetv:NI_1004933@Zouzous',
        'only_matching': True,
    }, {
        'url': 'francetv:NI_983319@Info-web',
        'only_matching': True,
    }, {
        'url': 'francetv:NI_983319',
        'only_matching': True,
    }, {
        'url': 'francetv:NI_657393@Regions',
        'only_matching': True,
    }, {
        # france-3 live
        'url': 'francetv:SIM_France3',
        'only_matching': True,
    }]

    def _extract_video(self, video_id, catalogue=None):
        # Videos are identified by idDiffusion so catalogue part is optional.
        # However when provided, some extra formats may be returned so we pass
        # it if available.

        info = {
            'title': None,
            'subtitle': None,
            'image': None,
            'subtitles': {},
            'duration': None,
            'videos': [],
            'formats': [],
        }

        def update_info(name, value):
            if (info[name] is None) and value:
                info[name] = value

        for device_type in ['desktop', 'mobile']:
            linfo = self._download_json(
                'https://player.webservices.francetelevisions.fr/v1/videos/%s' % video_id,
                video_id, 'Downloading %s video JSON' % device_type, query={
                    'device_type': device_type,
                    'browser': 'chrome',
                }, fatal=False)

            if linfo and linfo.get('video'):
                if linfo.get('meta'):
                    update_info('title', linfo['meta'].get('title'))
                    update_info('subtitle', linfo['meta'].get('additional_title'))
                    update_info('image', linfo['meta'].get('image_url'))
                if linfo['video'].get('url'):
                    if linfo['video'].get('drm'):
                        self._downloader.to_screen('This video source is DRM protected. Skipping')
                    else:
                        info['videos'].append(linfo['video'])
                        update_info('duration', linfo['video'].get('duration'))

        if len(info['videos']) == 0:
            raise ExtractorError(
                'No video source has been found',
                expected=True,
                video_id=video_id)

        allowed_countries = info['videos'][0].get('geoblocage')
        if allowed_countries:
            georestricted = True
            geo_info = self._download_json(
                'http://geo.francetv.fr/ws/edgescape.json', video_id,
                'Downloading geo restriction info')
            country = geo_info['reponse']['geo_info']['country_code']
            if country not in allowed_countries:
                raise ExtractorError(
                    'The video is not available from your location',
                    expected=True)
        else:
            georestricted = False

        def sign(manifest_url, manifest_id):
            for host in ('hdfauthftv-a.akamaihd.net', 'hdfauth.francetv.fr'):
                signed_url = url_or_none(self._download_webpage(
                    'https://%s/esi/TA' % host, video_id,
                    'Downloading signed %s manifest URL' % manifest_id,
                    fatal=False, query={
                        'url': manifest_url,
                    }))
                if signed_url:
                    return signed_url
            return manifest_url

        is_live = None

        for video in info['videos']:
            video_url = video.get('url')
            if not video_url:
                continue
            if is_live is None:
                is_live = (try_get(
                    video, lambda x: x['plages_ouverture'][0]['direct'], bool) is True
                    or video.get('is_live') is True
                    or '/live.francetv.fr/' in video_url)
            format_id = video.get('format')
            ext = determine_ext(video_url)
            if ext == 'f4m':
                if georestricted:
                    # See https://github.com/ytdl-org/youtube-dl/issues/3963
                    # m3u8 urls work fine
                    continue
                info['formats'].extend(self._extract_f4m_formats(
                    sign(video_url, format_id) + '&hdcore=3.7.0&plugin=aasp-3.7.0.39.44',
                    video_id, f4m_id=format_id, fatal=False))
            elif ext == 'm3u8':
                res = self._extract_m3u8_formats(
                    sign(video_url, format_id), video_id, 'mp4',
                    entry_protocol='m3u8_native', m3u8_id=format_id,
                    fatal=False, include_subtitles=True)
                if not res:
                    continue
                format, subtitle = res
                info['formats'].extend(format)
                for lang in subtitle:
                    if lang in info['subtitles']:
                        info['subtitles'][lang].extend(subtitle[lang])
                    else:
                        info['subtitles'][lang] = subtitle[lang]
            elif ext == 'mpd':
                info['formats'].extend(self._extract_mpd_formats(
                    sign(video_url, format_id), video_id, mpd_id=format_id, fatal=False))
            elif video_url.startswith('rtmp'):
                info['formats'].append({
                    'url': video_url,
                    'format_id': 'rtmp-%s' % format_id,
                    'ext': 'flv',
                })
            else:
                if self._is_valid_url(video_url, video_id, format_id):
                    info['formats'].append({
                        'url': video_url,
                        'format_id': format_id,
                    })

        for f in info['formats']:
            preference = 100
            if f['format_id'].startswith('dash-audio_qtz=96000') or (f['format_id'].find('Description') >= 0):
                preference = -1
            elif f['format_id'].startswith('dash-audio'):
                preference = 10
            elif f['format_id'].startswith('hls-audio'):
                preference = 200
            elif f['format_id'].startswith('dash-video'):
                preference = 50
            f['preference'] = preference

        self._sort_formats(info['formats'])

        if info['subtitle']:
            info['title'] += ' - %s' % info['subtitle']
        info['title'] = info['title'].strip()

        return {
            'id': video_id,
            'title': self._live_title(info['title']) if is_live else info['title'],
            'description': clean_html(info.get('synopsis')),
            'thumbnail': info.get('image'),
            'duration': int_or_none(info.get('duration')),
            'timestamp': int_or_none(try_get(info, lambda x: x['diffusion']['timestamp'])),
            'is_live': is_live,
            'formats': info['formats'],
            'subtitles': info['subtitles'],
        }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        catalog = mobj.group('catalog')

        if not video_id:
            qs = compat_urlparse.parse_qs(compat_urlparse.urlparse(url).query)
            video_id = qs.get('idDiffusion', [None])[0]
            catalog = qs.get('catalogue', [None])[0]
            if not video_id:
                raise ExtractorError('Invalid URL', expected=True)

        return self._extract_video(video_id, catalog)


class FranceTVSiteIE(FranceTVBaseInfoExtractor):
    _VALID_URL = r'https?://(?:(?:www\.)?france\.tv|mobile\.france\.tv)/(?:[^/]+/)*(?P<id>[^/]+)\.html'

    _TESTS = [{
        'url': 'https://www.france.tv/france-2/13h15-le-dimanche/140921-les-mysteres-de-jesus.html',
        'info_dict': {
            'id': 'ec217ecc-0733-48cf-ac06-af1347b849d1',
            'ext': 'mp4',
            'title': '13h15, le dimanche... - Les mystères de Jésus',
        },
        'params': {
            'skip_download': True,
            'format': 'bestvideo',
        },
        'add_ie': [FranceTVIE.ie_key()],
        'expected_warnings': 'Unknown MIME type application/mp4 in DASH manifest',
    }, {
        # france3
        'url': 'https://www.france.tv/france-3/des-chiffres-et-des-lettres/139063-emission-du-mardi-9-mai-2017.html',
        'only_matching': True,
    }, {
        # france4
        'url': 'https://www.france.tv/france-4/hero-corp/saison-1/134151-apres-le-calme.html',
        'only_matching': True,
    }, {
        # france5
        'url': 'https://www.france.tv/france-5/c-a-dire/saison-10/137013-c-a-dire.html',
        'only_matching': True,
    }, {
        # franceo
        'url': 'https://www.france.tv/france-o/archipels/132249-mon-ancetre-l-esclave.html',
        'only_matching': True,
    }, {
        # france2 live
        'url': 'https://www.france.tv/france-2/direct.html',
        'only_matching': True,
    }, {
        'url': 'https://www.france.tv/documentaires/histoire/136517-argentine-les-500-bebes-voles-de-la-dictature.html',
        'only_matching': True,
    }, {
        'url': 'https://www.france.tv/jeux-et-divertissements/divertissements/133965-le-web-contre-attaque.html',
        'only_matching': True,
    }, {
        'url': 'https://mobile.france.tv/france-5/c-dans-l-air/137347-emission-du-vendredi-12-mai-2017.html',
        'only_matching': True,
    }, {
        'url': 'https://www.france.tv/142749-rouge-sang.html',
        'only_matching': True,
    }, {
        # france-3 live
        'url': 'https://www.france.tv/france-3/direct.html',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)

        webpage = self._download_webpage(url, display_id)

        catalogue = None
        video_id = self._search_regex(
            r'(?:data-main-video\s*=|videoId["\']?\s*[:=])\s*(["\'])(?P<id>(?:(?!\1).)+)\1',
            webpage, 'video id', default=None, group='id')

        if not video_id:
            video_id, catalogue = self._html_search_regex(
                r'(?:href=|player\.setVideo\(\s*)"http://videos?\.francetv\.fr/video/([^@]+@[^"]+)"',
                webpage, 'video ID').split('@')

        return self._make_url_result(video_id, catalogue)


class FranceTVInfoIE(FranceTVBaseInfoExtractor):
    IE_NAME = 'francetvinfo.fr'
    _VALID_URL = r'https?://(?:www|mobile|france3-regions)\.francetvinfo\.fr/(?:[^/]+/)*(?P<id>[^/?#&.]+)'

    _TESTS = [{
        'url': 'https://www.francetvinfo.fr/replay-jt/france-3/soir-3/jt-grand-soir-3-lundi-26-aout-2019_3569073.html',
        'info_dict': {
            'id': 'e49f9ff0-2177-458e-830f-a28eccf19dd1',
            'ext': 'mp4',
            'title': 'Soir 3',
            'subtitles': {
                'fr': 'mincount:1',
            },
        },
        'params': {
            'skip_download': True,
            'format': 'dash-video=118000+dash-audio_fre=192000',
        },
        'add_ie': [FranceTVIE.ie_key()],
        'expected_warnings': 'Unknown MIME type application/mp4 in DASH manifest',
    }, {
        'url': 'http://www.francetvinfo.fr/elections/europeennes/direct-europeennes-regardez-le-debat-entre-les-candidats-a-la-presidence-de-la-commission_600639.html',
        'only_matching': True,
    }, {
        'url': 'http://www.francetvinfo.fr/economie/entreprises/les-entreprises-familiales-le-secret-de-la-reussite_933271.html',
        'only_matching': True,
    }, {
        'url': 'http://france3-regions.francetvinfo.fr/bretagne/cotes-d-armor/thalassa-echappee-breizh-ce-venredi-dans-les-cotes-d-armor-954961.html',
        'only_matching': True,
    }, {
        # Dailymotion embed
        'url': 'http://www.francetvinfo.fr/politique/notre-dame-des-landes/video-sur-france-inter-cecile-duflot-denonce-le-regard-meprisant-de-patrick-cohen_1520091.html',
        'md5': 'ee7f1828f25a648addc90cb2687b1f12',
        'info_dict': {
            'id': 'x4iiko0',
            'ext': 'mp4',
            'title': 'NDDL, référendum, Brexit : Cécile Duflot répond à Patrick Cohen',
            'description': 'Au lendemain de la victoire du "oui" au référendum sur l\'aéroport de Notre-Dame-des-Landes, l\'ancienne ministre écologiste est l\'invitée de Patrick Cohen. Plus d\'info : https://www.franceinter.fr/emissions/le-7-9/le-7-9-27-juin-2016',
            'timestamp': 1467011958,
            'upload_date': '20160627',
            'uploader': 'France Inter',
            'uploader_id': 'x2q2ez',
        },
        'add_ie': ['Dailymotion'],
        'params': {
            # TODO: the download currently fails (FORBIDDEN) - fix and complete the test
            'skip_download': True,
        },
    }, {
        'url': 'http://france3-regions.francetvinfo.fr/limousin/emissions/jt-1213-limousin',
        'only_matching': True,
    }, {
        # "<figure id=" pattern (#28792)
        'url': 'https://www.francetvinfo.fr/culture/patrimoine/incendie-de-notre-dame-de-paris/notre-dame-de-paris-de-l-incendie-de-la-cathedrale-a-sa-reconstruction_4372291.html',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)

        webpage = self._download_webpage(url, display_id)

        dailymotion_urls = DailymotionIE._extract_urls(webpage)
        if dailymotion_urls:
            return self.playlist_result([
                self.url_result(dailymotion_url, DailymotionIE.ie_key())
                for dailymotion_url in dailymotion_urls])

        video_id = self._search_regex(
            (r'player\.load[^;]+src:\s*["\']([^"\']+)',
             r'id-video=([^@]+@[^"]+)',
             r'<a[^>]+href="(?:https?:)?//videos\.francetv\.fr/video/([^@]+@[^"]+)"',
             r'(?:data-id|<figure[^<]+\bid)=["\']([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})'),
            webpage, 'video id')

        return self._make_url_result(video_id)
