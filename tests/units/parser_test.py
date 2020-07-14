# -*- coding: utf-8 -*-
"""
All unit tests for the scraper public API should be contained in this file.
"""

from scraper.patterns import get_voltage, get_email, get_mobile_number
from tests.conftest import print_test
from scraper.parser import Parser
import re

# https://www.power-technology.com/projects/dai-nanh/

def test_parser(fixture_directory):
    allow_tags = [
        'a', 'span', 'p', 'br', 'strong', 'b',
        'em', 'i', 'tt', 'code', 'pre', 'blockquote', 'img', 'h1',
        'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd'
    ]
    with open(fixture_directory + "/html/cnn_article.html") as f:
        html1 = f.read()
    html2 = Parser.get_unicode_html(html1)
    assert html1 == html2
    doc1 = Parser.from_string(html1)
    Parser.strip_tags(doc1, 'b', 'strong', 'i', 'br', 'sup')
    html3 = Parser.outer_html(doc1)
    doc2 = Parser.clean_article_html(doc1)
    child_nodes = Parser.child_nodes_with_text(doc2)
    len1 = len(child_nodes)
    assert len1
    text = Parser.get_text(doc2)
    pass