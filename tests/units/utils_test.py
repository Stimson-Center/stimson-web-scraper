# -*- coding: utf-8 -*-
"""
All unit tests for the scraper public API should be contained in this file.
"""

from scraper.utils import get_languages, get_available_language_codes, get_available_languages
from tests.conftest import print_test


@print_test
def test_languages_api_call():
    languages = get_languages()
    assert languages
    codes = get_available_language_codes()
    assert codes
    languages = get_available_languages()
    assert languages
