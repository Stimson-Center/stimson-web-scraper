# -*- coding: utf-8 -*-
"""
All unit tests for the scraper library should be contained in this file.
"""
import os
import re

from scraper.urls import extract_domain
from tests.conftest import print_test

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.abspath(os.path.join(TEST_DIR, '../fixtures'))


@print_test
def test_valid_urls():
    """Prints out a list of urls with our heuristic guess if it is a
    valid news url purely based on the url
    """
    from scraper.urls import valid_url

    with open(os.path.join(FIXTURES_DIR, 'url/test_list.txt'), 'r') as f:
        lines = f.readlines()
        test_tuples = [tuple(line.strip().split(' ')) for line in lines]
        # tuples are ('1', 'url_goes_here') form, '1' means valid,
        # '0' otherwise

    for lst, url in test_tuples:
        truth_val = bool(int(lst))
        try:
            assert truth_val == valid_url(url, test=True)
        except AssertionError:
            print('\t\turl: %s is supposed to be %s' % (url, truth_val))
            raise


@print_test
def test_pubdate():
    """Checks that irrelevant data in url isn't considered as publishing date"""
    from scraper.urls import STRICT_DATE_REGEX

    with open(os.path.join(FIXTURES_DIR, 'url/test_pubdate.txt'), 'r') as f:
        lines = f.readlines()
        test_tuples = [tuple(line.strip().split(' ')) for line in lines]
        # tuples are ('1', 'url_goes_here') form, '1' means publishing date
        # is present in the url, '0' otherwise

        for pubdate, url in test_tuples:
            is_present = bool(int(pubdate))
            date_match = re.search(STRICT_DATE_REGEX, url)
            try:
                assert is_present == bool(date_match)
            except AssertionError:
                if is_present:
                    print('\t\tpublishing date in %s should be present' % url)
                else:
                    print('\t\tpublishing date in %s should not be present' % url)
                raise


@print_test
def test_prepare_url():
    """Normalizes a url, removes arguments, hashtags. If a relative url, it
    merges it with the source domain to make an abs url, etc
    """
    from scraper.urls import prepare_url

    with open(os.path.join(FIXTURES_DIR, 'url/test_prepare.txt'), 'r') as f:
        lines = f.readlines()
        test_tuples = [tuple(line.strip().split(' ')) for line in lines]
        # tuples are ('real_url', 'url_path', 'source_url') form

    for real, url, source in test_tuples:
        try:
            prepared_url = prepare_url(url, source)
            assert real.startswith(prepared_url)
        except AssertionError:
            print('\t\turl: %s + %s is supposed to be %s' % (url, source, real))
            raise


@print_test
def test_extract_domain():
    tld, subd = extract_domain("https://www.cnn.com")
    assert subd == 'www'
    assert tld == 'cnn'

    tld, subd = extract_domain("https://cnn.com")
    assert subd == ''
    assert tld == 'cnn'
