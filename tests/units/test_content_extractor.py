# -*- coding: utf-8 -*-
"""
All unit tests for the content extractors should be contained in this file.
"""

from scraper import Configuration
from scraper.content_extractor import ContentExtractor
from scraper.parser import Parser

"""Test specific element extraction cases"""


# noinspection PyPep8Naming
def setUp():
    extractor = ContentExtractor(Configuration())
    parser = Parser
    return extractor, parser


def _get_title(html):
    extractor, parser = setUp()
    doc = parser.fromstring(html)
    return extractor.get_title(doc)


def test_get_title_basic():
    html = '<title>Test title</title>'
    assert _get_title(html) == 'Test title'


def test_get_title_split():
    html = '<title>Test page » Test title</title>'
    assert _get_title(html) == 'Test title'


def test_get_title_split_escaped():
    html = '<title>Test page &raquo; Test title</title>'
    assert _get_title(html) == 'Test title'


def test_get_title_quotes():
    title = 'Test page and «something in quotes»'
    html = '<title>{}</title>'.format(title)
    assert _get_title(html) == title


def _get_canonical_link(article_url, html):
    extractor, parser = setUp()
    doc = parser.fromstring(html)
    return extractor.get_canonical_link(article_url, doc)


def test_get_canonical_link_rel_canonical():
    url = 'http://www.example.com/article.html'
    html = '<link rel="canonical" href="{}">'.format(url)
    assert _get_canonical_link('', html) == url


def test_get_canonical_link_rel_canonical_absolute_url():
    url = 'http://www.example.com/article.html'
    html = '<link rel="canonical" href="article.html">'
    article_url = 'http://www.example.com/article?foo=bar'
    assert _get_canonical_link(article_url, html) == url


def test_get_canonical_link_og_url_absolute_url():
    url = 'http://www.example.com/article.html'
    html = '<meta property="og:url" content="article.html">'
    article_url = 'http://www.example.com/article?foo=bar'
    assert _get_canonical_link(article_url, html) == url


def test_get_canonical_link_hostname_og_url_absolute_url():
    url = 'http://www.example.com/article.html'
    html = '<meta property="og:url" content="www.example.com/article.html">'
    article_url = 'http://www.example.com/article?foo=bar'
    assert _get_canonical_link(article_url, html) == url


def test_get_top_image_from_meta():
    extractor, parser = setUp()
    html = '<meta property="og:image" content="https://example.com/meta_img_filename.jpg" />' \
           '<meta name="og:image" content="https://example.com/meta_another_img_filename.jpg"/>'
    html_empty_og_content = '<meta property="og:image" content="" />' \
                            '<meta name="og:image" content="https://example.com/meta_another_img_filename.jpg"/>'
    html_empty_all = '<meta property="og:image" content="" />' \
                     '<meta name="og:image" />'
    html_rel_img_src = html_empty_all + '<link rel="img_src" href="https://example.com/meta_link_image.jpg" />'
    html_rel_img_src2 = html_empty_all + '<link rel="image_src" href="https://example.com/meta_link_image2.jpg" />'
    html_rel_icon = html_empty_all + '<link rel="icon" href="https://example.com/meta_link_rel_icon.ico" />'

    doc = parser.fromstring(html)
    assert extractor.get_meta_img_url('http://www.example.com/article?foo=bar',
                                      doc) == 'https://example.com/meta_img_filename.jpg'

    doc = parser.fromstring(html_empty_og_content)
    assert extractor.get_meta_img_url('http://www.example.com/article?foo=bar',
                                      doc) == 'https://example.com/meta_another_img_filename.jpg'

    doc = parser.fromstring(html_empty_all)
    assert extractor.get_meta_img_url('http://www.example.com/article?foo=bar', doc) == ''

    doc = parser.fromstring(html_rel_img_src)
    assert extractor.get_meta_img_url('http://www.example.com/article?foo=bar',
                                      doc) == 'https://example.com/meta_link_image.jpg'

    doc = parser.fromstring(html_rel_img_src2)
    assert extractor.get_meta_img_url('http://www.example.com/article?foo=bar',
                                      doc) == 'https://example.com/meta_link_image2.jpg'

    doc = parser.fromstring(html_rel_icon)
    assert extractor.get_meta_img_url('http://www.example.com/article?foo=bar',
                                      doc) == 'https://example.com/meta_link_rel_icon.ico'
