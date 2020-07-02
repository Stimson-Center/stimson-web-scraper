# -*- coding: utf-8 -*-
"""
All unit tests for the scraper public API should be contained in this file.
"""

from scraper.patterns import get_voltage, get_email, get_mobile_number
from tests.conftest import print_test
from scraper.parser import Parser


# https://www.power-technology.com/projects/dai-nanh/

def test_parser(fixture_directory):
    allow_tags = [
        'a', 'span', 'p', 'br', 'strong', 'b',
        'em', 'i', 'tt', 'code', 'pre', 'blockquote', 'img', 'h1',
        'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd'
    ]
    with open(fixture_directory + "/html/cnn_article.html") as f:
        html = f.read()
    html2 = Parser.get_unicode_html(html)
    assert html == html2
    doc = Parser.from_string(html)
    x = Parser.clean_article_html(doc)
    pass