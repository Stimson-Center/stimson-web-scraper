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


def test_focustaiwan_tw():
    url = "https://focustaiwan.tw/society/201606280011"
    article = validate(url, 'en', False)


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
    article = validate(url, 'en', False)


def test_chinese_good():
    url = 'http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml'
    validate(url, 'zh', False)
    url = "http://news.sohu.com/20050601/n225789219.shtml"
    article = validate(url, 'zh', True)


def test_pubdate():
    url = "https://www.theglobeandmail.com/news/world/airasia-search/article22224253/"
    url = "http://www.telegraph.co.uk/news/politics/margaret-thatcher/11313354/Margaret-Thatcher-feared-GCSEs-would-lower-school-standards.html"
    article = validate(url, 'en', False)


def test_ner():
    url = "https://www.power-technology.com/projects/dai-nanh/"
    article = validate(url, 'en', False)


def test_cnn():
    url = "https://bleacherreport.com/articles/2897910-bubba-wallace-says-hes-wore-the-hell-out-after-nascar-noose-investigation?utm_source=cnn.com&utm_medium=referral&utm_campaign=editorial"
    article = validate(url, 'en', False)
    pass


def test_pdf_missing_authors():
    url = "https://oceanpanel.org/sites/default/files/2020-02/HLP%20Blue%20Paper%20on%20IUU%20Fishing%20and%20Associated%20Drivers.pdf"
    article = validate(url, 'en', False)
    pass


def test_pdf_duplicate_keywords_ignore_case():
    url = "https://oceanpanel.org/sites/default/files/2020-02/HLP%20Blue%20Paper%20on%20IUU%20Fishing%20and%20Associated%20Drivers.pdf"
    article = validate(url, 'en', False)
    pass