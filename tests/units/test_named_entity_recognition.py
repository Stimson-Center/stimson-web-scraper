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

def test_power_projects_english():
    url = "https://www.power-technology.com/projects/dai-nanh/"
    validate(url, 'en', False)

def test_chinese():
    url = "http://news.sohu.com/20050601/n225789219.shtml"
    article = validate(url, 'zh', False)
    assert article
