# -*- coding: utf-8 -*-
"""
All unit tests for the scraper pdf processing should be contained in this file.
"""
import pytest

from scraper import Article, Configuration
from tests.conftest import print_test


@print_test
def test_article_pdf_ignoring():
    config = Configuration()
    empty_pdf = "%PDF-"  # empty PDF constant
    config.ignored_content_types_defaults = {"application/pdf": empty_pdf,
                                             "application/x-pdf": empty_pdf,
                                             "application/x-bzpdf": empty_pdf,
                                             "application/x-gzpdf": empty_pdf}
    article = Article(
        url='https://www.adobe.com/pdf/pdfs/ISO32000-1PublicPatentLicense.pdf',
        config=config
    )
    article.download()
    assert empty_pdf == article.html


@print_test
def test_article_pdf_fetching():
    article = Article(url='https://www.adobe.com/pdf/pdfs/ISO32000-1PublicPatentLicense.pdf')
    article.build()
    assert not article.html.startswith('%PDF-')
    assert len(article.keywords)
    assert len(article.authors)
    assert article.publish_date
    assert article.summary
    assert len(article.text) > len(article.summary)
    assert article.text
    assert article.url


@pytest.mark.options(debug=True)
def test_article_to_pdf(fixture_directory, client):
    import os
    import json
    test_driver_file = os.path.join(fixture_directory,
                                    "json",
                                    "2015-09-29 Myawaddy industrial zone set for 2017 opening.en.json")
    with open(test_driver_file) as f:
        payload = json.load(f)
        language = payload['language']
        response = client.post("/pdf", json=payload)
        assert 200 == response.status_code
        assert '200 OK' == response.status
        assert 'utf-8' == response.charset
        assert response.data
        output = f"/tmp/{payload['publish_date']}_{payload['title']}.{language}.pdf"
        with open(output, 'wb') as f:
            f.write(response.data)