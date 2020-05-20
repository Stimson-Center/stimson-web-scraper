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
        assert len(sources.article.title)
        # article as a dictionary
        # https://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
        article_dict = vars(sources.article)
        print(f'{elapsed_time} seconds, {sources.article.title} urls, at: {website["url"]}')
        # print(f'{sources.article.text} text')
