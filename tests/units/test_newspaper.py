# -*- coding: utf-8 -*-

import newspaper
from time import time
from newspaper.configuration import Configuration


# noinspection PyUnresolvedReferences
def test_newspapers():
    websites = [
        {"url": "https://www.cnn.com", "language": "en"},
        {"url": "https://www.yahoo.com", "language": "en"},
        {"url": "https://www.sina.com.cn", "language": "zh"},
        {"url": "http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml",
         "language": "zh"},
        {"url": "https://academic.oup.com/jrs/article-abstract/24/1/23/1595471", "language": "en"},
        {"url": "https://www.theatlantic.com/politics/archive/2018/02/pageantry-military-parades/552953/",
         "language": "en"}
    ]
    print("\n")
    config = Configuration()
    config.memoize_articles = False
    for website in websites:
        # set variables
        start_time = time()
        np = newspaper.build(website["url"], config=config, language=website["language"])
        assert len(np.articles)
        end_time = time()
        elapsed_time = end_time - start_time
        print(f'{elapsed_time} seconds, {len(np.articles)} urls, at: {website["url"]}')
        pass
