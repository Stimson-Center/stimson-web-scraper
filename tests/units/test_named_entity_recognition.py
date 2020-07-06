# -*- coding: utf-8 -*-
"""
All unit tests for the scraper Article should be contained in this file.
"""

import spacy

from scraper import Article, Configuration
from scraper.named_entity_recognition import TextRank4Keyword
from scraper.text import get_stopwords


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


def test_methods():
    nlp = spacy.load("en_core_web_sm")
    # use spacy language specific STOP WORDS
    stopwords = get_stopwords("en")
    tr4w = TextRank4Keyword(nlp)
    text = "Alan Cooper\nTemple University\nB.A.\nemail:\tcooper@pobox.com\nmobile:+1555.555.5555"
    tr4w.analyze(text, candidate_pos=['NOUN', 'PROPN'], window_size=4, lower=False, stopwords=stopwords)
    education = tr4w.get_education()
    assert education == ["BA"]
    persons = tr4w.get_persons()
    assert len(persons) == 1
    assert "Alan Cooper" in persons


def test_dates():
    date_format = "%Y-%m-%d"
    nlp = spacy.load("en_core_web_sm")
    # use spacy language specific STOP WORDS
    stopwords = get_stopwords("en")
    tr4w = TextRank4Keyword(nlp)
    date_sentences = [
        "I departed that city on 01/04/1937",
        "I arrived in that city on January 4, 1937",
        "commencing on January 4, 1937, (the “Lease Commencement Date”)",
        "Saturday January 4, 1937",
        "I departed that city on 1937-01-04"
    ]
    for text in date_sentences:
        tr4w.analyze(text, candidate_pos=['NOUN', 'PROPN'], window_size=4, lower=False, stopwords=stopwords)
        dates = tr4w.get_dates()
        date = dates[0].strftime(date_format)
        assert date == "1937-01-04"

    tr4w.analyze("I arrived in that city in 1937", candidate_pos=['NOUN', 'PROPN'], window_size=4, lower=False,
                 stopwords=stopwords)
    dates = tr4w.get_dates()
    assert dates[0].year == 1937

    nlp = spacy.load("ja_core_news_sm")
    stopwords = get_stopwords("ja")
    tr4w = TextRank4Keyword(nlp)
    date_sentences = [
        "1937年1月4日"
    ]
    for text in date_sentences:
        tr4w.analyze(text, candidate_pos=['NOUN', 'PROPN'], window_size=4, lower=False, stopwords=stopwords)
        dates = tr4w.get_dates()
        date = dates[0].strftime(date_format)
        assert date == "1937-01-04"


def test_power_projects_english():
    url = "https://www.power-technology.com/projects/dai-nanh/"
    article = validate(url, 'en', False)


def test_chinese():
    url = "http://news.sohu.com/20050601/n225789219.shtml"
    article = validate(url, 'zh', False)
    assert article


def test_alphanum_keywords():
    url = "http://bangkokpost.com/world/1249738/casting-a-wider-net"
    article = validate(url, 'en', False)
    for keyword in article.keywords:
        assert keyword.isalnum()
