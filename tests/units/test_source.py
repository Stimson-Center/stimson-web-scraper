# -*- coding: utf-8 -*-
"""
All unit tests for the news feeds should be contained in this file.
"""

from scraper import Source
from scraper.source import Category
from tests.conftest import print_test, mock_resource_with


@print_test
def test_source_url_input_none():
    try:
        Source(url=None)
    except Exception as ex:
        assert ex.args[0] == 'Input url is bad!'


@print_test
def test_source_build():
    """
    builds a source object, validates it has no errors, prints out
    all valid categories and feed urls
    """
    DESC = ('CNN.com International delivers breaking news from across '
            'the globe and information on the latest top stories, '
            'business, sports and entertainment headlines. Follow the '
            'news as it happens through: special reports, videos, '
            'audio, photo galleries plus interactive maps and timelines.')
    CATEGORY_URLS = [
        'http://cnn.com/ASIA', 'http://connecttheworld.blogs.cnn.com',
        'http://cnn.com/HLN', 'http://cnn.com/MIDDLEEAST',
        'http://cnn.com', 'http://ireport.cnn.com',
        'http://cnn.com/video', 'http://transcripts.cnn.com',
        'http://cnn.com/espanol',
        'http://partners.cnn.com', 'http://www.cnn.com',
        'http://cnn.com/US', 'http://cnn.com/EUROPE',
        'http://cnn.com/TRAVEL', 'http://cnn.com/cnni',
        'http://cnn.com/SPORT', 'http://cnn.com/mostpopular',
        'http://arabic.cnn.com', 'http://cnn.com/WORLD',
        'http://cnn.com/LATINAMERICA', 'http://us.cnn.com',
        'http://travel.cnn.com', 'http://mexico.cnn.com',
        'http://cnn.com/SHOWBIZ', 'http://edition.cnn.com',
        'http://amanpour.blogs.cnn.com', 'http://money.cnn.com',
        'http://cnn.com/tools/index.html', 'http://cnnespanol.cnn.com',
        'http://cnn.com/CNNI', 'http://business.blogs.cnn.com',
        'http://cnn.com/AFRICA', 'http://cnn.com/TECH',
        'http://cnn.com/BUSINESS']
    FEEDS = ['http://rss.cnn.com/rss/edition.rss']
    BRAND = 'cnn'

    s = Source('http://cnn.com', verbose=False, memoize_articles=False)
    # html = mock_resource_with('http://cnn.com', 'cnn_main_site')
    s.clean_memo_cache()
    s.build()

    # TODO: The rest of the source extraction features will be fully tested
    # after I figure out a way to sensibly mock the HTTP requests for all
    # of the category and feeed URLs

    # assert s.brand == BRAND
    # assert s.description == DESC
    # assert s.size() == 266
    # assert s.category_urls() == CATEGORY_URLS

    # TODO: A lot of the feed extraction is NOT being tested because feeds
    # are primarly extracted from the HTML of category URLs. We lose this
    # effect by just mocking CNN's main page HTML. Warning: tedious fix.
    # assert s.feed_urls() == FEEDS


@print_test
def test_cache_categories():
    """Builds two same source objects in a row examines speeds of both
    """
    url = 'http://uk.yahoo.com'
    html = mock_resource_with('yahoo_main_site', 'html')
    s = Source(url)
    s.download()
    s.parse()
    s.set_categories()

    saved_urls = s.category_urls()
    s.categories = []
    s.set_categories()
    assert len(saved_urls) == len(s.category_urls())


@print_test
def test_feed_extraction():
    """Test that feeds are matched properly
    """
    url = 'http://theatlantic.com'
    html = mock_resource_with('theatlantic.com1', 'html')
    s = Source(url, memoize_articles=False)
    s.html = html
    s.parse()
    # mock in categories containing only homepage
    # s.set_categories()
    category = Category(url=url)
    category.html = html
    category.doc = s.doc
    s.categories = [category, ]
    # s.parse_categories()
    s.set_feeds()
    assert len(s.feeds) == 3
