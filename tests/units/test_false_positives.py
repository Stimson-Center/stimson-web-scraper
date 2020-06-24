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


def test_focustaiwan_tw():
    url = "https://focustaiwan.tw/society/201606280011"
    validate(url, 'en', False)


def test_allafrica_com():
    url = "https://allafrica.com/stories/201602041393.html"
    # curl http://allafrica.com/stories/201602041393.html
    # <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    # <html><head>
    # <title>301 Moved Permanently</title>
    # </head><body>
    # <h1>Moved Permanently</h1>
    # <p>The document has moved <a href="https://allafrica.com/stories/201602041393.html">here</a>.</p>
    # </body></html>
    validate(url, 'en', False)


def test_chinese_good():
    url = 'http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml'
    validate(url, 'zh', False)
    url = "http://news.sohu.com/20050601/n225789219.shtml"
    validate(url, 'zh', True)


def test_pubdate():
    url = "https://www.theglobeandmail.com/news/world/airasia-search/article22224253/"
    url = "http://www.telegraph.co.uk/news/politics/margaret-thatcher/11313354/Margaret-Thatcher-feared-GCSEs-would-lower-school-standards.html"
    validate(url, 'en', False)

def test_ner():
    url = "https://www.power-technology.com/projects/dai-nanh/"
    validate(url, 'en', False)
    pass