# -*- coding: utf-8 -*-
"""
All unit tests for the scraper public API should be contained in this file.
"""

import scraper
from scraper.utils import get_languages, get_available_languages
from tests.conftest import print_test


@print_test
def test_hot_trending():
    """Grab google trending, just make sure this runs
    """
    trends = scraper.hot()
    assert trends


@print_test
def test_popular_urls():
    """Just make sure this method runs
    """
    urls = scraper.popular_urls()
    assert len(urls)


@print_test
def test_languages_api_call():
    language_dict = get_languages()
    assert language_dict
    codes = get_available_languages()
    assert codes
    scraper.languages()
