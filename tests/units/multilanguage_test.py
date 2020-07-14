# -*- coding: utf-8 -*-
"""
All unit tests for multi languages should be contained in this file.
"""

from scraper import Article, fulltext
from tests.conftest import print_test, mock_resource_with


@print_test
def test_chinese_fulltext_extract():
    url = 'http://news.sohu.com/20050601/n225789219.shtml'
    article = Article(url=url, language='zh')
    html = mock_resource_with('chinese_article', 'html')
    article.download(html)
    article.parse()
    text = mock_resource_with('chinese', 'txt')
    assert text == article.text
    assert text == fulltext(article.html, 'zh')


@print_test
def test_arabic_fulltext_extract():
    url = 'http://arabic.cnn.com/2013/middle_east/8/3/syria.clashes/' \
          'index.html'
    article = Article(url=url)
    html = mock_resource_with('arabic_article', 'html')
    article.download(html)
    article.parse()
    assert 'ar' == article.meta_lang
    text = mock_resource_with('arabic', 'txt')
    assert text == article.text
    assert text == fulltext(article.html, 'ar')


@print_test
def test_spanish_fulltext_extract():
    url = 'http://ultimahora.es/mallorca/noticia/noticias/local/fiscal' \
          'ia-anticorrupcion-estudia-recurre-imputacion-infanta.html'
    article = Article(url=url, language='es')
    html = mock_resource_with('spanish_article', 'html')
    article.download(html)
    article.parse()
    text = mock_resource_with('spanish', 'txt')
    assert text == article.text
    assert text == fulltext(article.html, 'es')


@print_test
def test_japanese_fulltext_extract():
    url = 'https://www.nikkei.com/article/DGXMZO31897660Y8A610C1000000/?n_cid=DSTPCS001'
    article = Article(url=url, language='ja')
    html = mock_resource_with('japanese_article', 'html')
    article.download(html)
    article.parse()
    text = mock_resource_with('japanese', 'txt')
    assert text == article.text
    assert text == fulltext(article.html, 'ja')


@print_test
def test_japanese_fulltext_extract2():
    url = 'http://www.afpbb.com/articles/-/3178894'
    article = Article(url=url, language='ja')
    html = mock_resource_with('japanese_article2', 'html')
    article.download(html)
    article.parse()
    text = mock_resource_with('japanese2', 'txt')
    assert text == article.text
    assert text == fulltext(article.html, 'ja')


@print_test
def test_thai_fulltext_extract():
    url = 'https://prachatai.com/journal/2019/01/80642'
    article = Article(url=url, language='th')
    html = mock_resource_with('thai_article', 'html')
    article.download(html)
    article.parse()
    text = mock_resource_with('thai', 'txt')
    assert text == article.text
    assert text == fulltext(article.html, 'th')


@print_test
def test_thai_pdf_extract():
    article = Article(
        url="http://tpch-th.listedcompany.com/misc/ShareholderMTG/egm201701/20170914-tpch-egm201701-enc02-th.pdf",
        language='th')
    article.build()
    assert not article.html.startswith('%PDF-')
    assert len(article.keywords)
    assert len(article.authors)
    assert article.publish_date
    assert article.summary
    assert len(article.text) > len(article.summary)
    assert article.text
    assert article.url


def test_hindi_news():
    url = "https://www.indiatv.in/maharashtra/maharashtra-coronavirus-latest-update-news-721708"
    article = Article(url=url, language='hi')
    article.download()
    article.parse()
    article.nlp()
    assert len(article.keywords)
    assert len(article.authors)
    # assert article.publish_date
    assert article.summary
    assert article.text
    assert len(article.summary) <= len(article.text)
    assert article.url


def test_arabic_news():
    url = "https://www.bbc.com/arabic/live/53203730"
    article = Article(url=url, language='ar')
    article.download()
    article.parse()
    article.nlp()
    assert len(article.keywords)
    assert len(article.authors)
    # assert article.publish_date
    assert article.summary
    assert article.text
    # assert len(article.summary) <= len(article.text)
    assert article.url