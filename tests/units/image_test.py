# -*- coding: utf-8 -*-
"""
All unit tests for the scraper Article should be contained in this file.
"""
import os
import unittest

from scraper.image_extractor import fetch_url
from scraper.version import __version__

from tests.conftest import print_test, mock_resource_with

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.abspath(os.path.join(TEST_DIR, '../fixtures'))
HTML_FN = os.path.abspath(os.path.join(FIXTURES_DIR, 'html'))


class ImageTestCase(unittest.TestCase):

    @print_test
    def test_url(self):
        url = 'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png'
        useragent = f'scraper/{__version__}'
        fetch_url(url, useragent)
