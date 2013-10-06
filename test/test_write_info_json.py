#!/usr/bin/env python
# coding: utf-8

import json
import os
import sys
import unittest

# Allow direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import youtube_dl.YoutubeDL
import youtube_dl.extractor
from youtube_dl.utils import *

PARAMETERS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "parameters.json")

# General configuration (from __init__, not very elegant...)
jar = compat_cookiejar.CookieJar()
cookie_processor = compat_urllib_request.HTTPCookieProcessor(jar)
proxy_handler = compat_urllib_request.ProxyHandler()
opener = compat_urllib_request.build_opener(
    proxy_handler, cookie_processor, YoutubeDLHandler())
compat_urllib_request.install_opener(opener)


class YoutubeDL(youtube_dl.YoutubeDL):

    def __init__(self, *args, **kwargs):
        super(YoutubeDL, self).__init__(*args, **kwargs)
        self.to_stderr = self.to_screen

with io.open(PARAMETERS_FILE, encoding='utf-8') as pf:
    params = json.load(pf)
params['writeinfojson'] = True
params['skip_download'] = True
params['writedescription'] = True

TEST_ID = 'BaW_jenozKc'
INFO_JSON_FILE = TEST_ID + '.mp4.info.json'
DESCRIPTION_FILE = TEST_ID + '.mp4.description'
EXPECTED_DESCRIPTION = u'''test chars:  "'/\ä↭𝕐

This is a test video for youtube-dl.

For more information, contact phihag@phihag.de .'''


class TestInfoJSON(unittest.TestCase):

    def setUp(self):
        # Clear old files
        self.tearDown()

    def test_info_json(self):
        ie = youtube_dl.extractor.YoutubeIE()
        ydl = YoutubeDL(params)
        ydl.add_info_extractor(ie)
        ydl.download([TEST_ID])
        self.assertTrue(os.path.exists(INFO_JSON_FILE))
        with io.open(INFO_JSON_FILE, 'r', encoding='utf-8') as jsonf:
            jd = json.load(jsonf)
        self.assertEqual(jd['upload_date'], u'20121002')
        self.assertEqual(jd['description'], EXPECTED_DESCRIPTION)
        self.assertEqual(jd['id'], TEST_ID)
        self.assertEqual(jd['extractor'], 'youtube')
        self.assertEqual(jd['title'], u'''youtube-dl test video "'/\ä↭𝕐''')
        self.assertEqual(jd['uploader'], 'Philipp Hagemeister')

        self.assertTrue(os.path.exists(DESCRIPTION_FILE))
        with io.open(DESCRIPTION_FILE, 'r', encoding='utf-8') as descf:
            descr = descf.read()
        self.assertEqual(descr, EXPECTED_DESCRIPTION)

    def test_info_json_with_stdout_as_output_returns_good_json(self):
        params['writedescription'] = False
        params['quiet'] = True
        params['outtmpl'] = '-'

        jd = None
        if sys.version_info < (3, 0):
            from subprocess import Popen, PIPE
            import shlex
            tests_dir = os.path.dirname(os.path.realpath(__file__))
            repo_dir = os.path.dirname(tests_dir)
            os.chdir(repo_dir)
            cmd = "youtube_dl/__main__.py --skip-download --write-info-json -quite BaW_jenozKc -o -"
            output = Popen(shlex.split(cmd), stdout=PIPE).communicate()[0]
            jd = json.loads(output)
        else:
            from unittest.mock import patch
            from io import StringIO
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ie = youtube_dl.extractor.YoutubeIE()
                ydl = YoutubeDL(params)
                ydl.add_info_extractor(ie)
                ydl.download([TEST_ID])
                output = mock_stdout.getvalue()
                jd = json.loads(output)

        self.assertEqual(jd['upload_date'], u'20121002')
        self.assertEqual(jd['description'], EXPECTED_DESCRIPTION)
        self.assertEqual(jd['id'], TEST_ID)
        self.assertEqual(jd['extractor'], 'youtube')
        self.assertEqual(jd['title'], u'''youtube-dl test video "'/\ä↭𝕐''')
        self.assertEqual(jd['uploader'], 'Philipp Hagemeister')

    def tearDown(self):
        if os.path.exists(INFO_JSON_FILE):
            os.remove(INFO_JSON_FILE)
        if os.path.exists(DESCRIPTION_FILE):
            os.remove(DESCRIPTION_FILE)

if __name__ == '__main__':
    unittest.main()
