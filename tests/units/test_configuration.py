# -*- coding: utf-8 -*-
"""
All unit tests for the scraper configuration options should be contained in this file.
"""

from scraper import Article, Source
from tests.conftest import print_test


# Tests if our **kwargs to config building setup actually works.
# NOTE: No need to mock responses as we are just initializing the
# objects, not actually calling download(..)
@print_test
def test_article_default_params():
    a = Article(url='http://www.cnn.com/2013/11/27/travel/weather-thanksgiving/index.html')
    assert 'en' == a.config.language
    assert a.config.memoize_articles
    assert a.config.use_meta_language


@print_test
def test_article_custom_params():
    a = Article(url='http://www.cnn.com/2013/11/27/travel/weather-thanksgiving/index.html',
                language='zh',
                memoize_articles=False)
    assert 'zh' == a.config.language
    assert not a.config.memoize_articles
    assert not a.config.use_meta_language


@print_test
def test_source_default_params():
    s = Source(url='http://cnn.com')
    assert 'en' == s.config.language
    assert 20000 == s.config.MAX_FILE_MEMO
    assert s.config.memoize_articles
    assert s.config.use_meta_language


@print_test
def test_source_custom_params():
    s = Source(url="http://cnn.com", memoize_articles=False,
               MAX_FILE_MEMO=10000, language='en')
    assert not s.config.memoize_articles
    assert 10000 == s.config.MAX_FILE_MEMO
    assert 'en' == s.config.language
    assert not s.config.use_meta_language
