# -*- coding: utf-8 -*-

from time import time

from scraper import Sources


# noinspection PyUnresolvedReferences
def test_sources():
    websites = [
        {"url": "https://www.cnn.com", "language": "en"},
        {"url": "https://www.yahoo.com", "language": "en"},
        {"url": "https://www.sina.com.cn", "language": "zh"},
        {"url": "http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml",
         "language": "zh"},
        {"url": "https://academic.oup.com/jrs/article-abstract/24/1/23/1595471", "language": "en"},
        {"url": "https://www.theatlantic.com/politics/archive/2018/02/pageantry-military-parades/552953/",
         "language": "en"},
        {"url": "http://kisugargroup.com/EN/product-energy-business.html", "language": "en"},
    ]
    print("\n")
    for website in websites:
        # set variables
        start_time = time()
        sources = Sources(website['url'], language=website['language'])
        sources.build()
        end_time = time()
        elapsed_time = end_time - start_time
        if sources.article and sources.article.title:
            assert len(sources.article.title)
            # https://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
            print(f'{elapsed_time} seconds, {sources.article.url} urls, at: {website["url"]}')
        else:
            # https://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
            print(f'{elapsed_time} seconds at: {website["url"]}')


# noinspection PyUnresolvedReferences
def test_sources_articles():
    sources = Sources("https://opendevelopmentcambodia.net/profiles/special-economic-zones", language="en")
    articles = sources.get_articles()
    category_articles = sources.get_categories()
    pass