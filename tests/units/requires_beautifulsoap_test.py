# -*- coding: utf-8 -*-
"""
All unit tests for the scraper Article should be contained in this file.
"""

from scraper import Article, Configuration


def validate(url, language, translate):
    config = Configuration()
    config.follow_meta_refresh = True
    # BUG was that website reported language as zh-Hant-TW when it really was en!
    config.use_meta_language = False
    config.set_language(language)
    config.translate = translate
    config.http_success_only = False
    article = Article(url, config=config)
    article.download()
    article.parse()
    assert len(article.text)
    article.nlp()
    return article


def test_gnana_news(fixture_directory):
    url = "https://newsghana.com.gh/17-fishermen-in-custody-for-illegal-fishing/"
    # url = "https://www.yahoo.com"
    article = validate(url, 'en', False)


def test_spanish_news():
    url = "https://www.elespectador.com/noticias/nacional/embarcacion-nicaragueense-realizaba-pesca-ilegal-aguas-articulo-616181"
    url = "https://www.elespectador.com/noticias/nacional/embarcacion-nicaraguense-realizaba-pesca-ilegal-en-aguas-colombianas/"
    article = Article(url=url, language='es')
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


def test_horseedmedia():
    url = "https://horseedmedia.net/2016/03/05/detained-illegal-fishing-vessel-escapes-northern-somalia-port/"
    article = validate(url, 'en', False)

def test1():
    url = "https://www.cnn.com/2020/06/30/media/mary-trump-book/index.html"
    article = validate(url, 'en', False)
