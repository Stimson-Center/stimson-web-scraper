# -*- coding: utf-8 -*-
"""
All unit tests for the scraper multi threading should be contained in this file.
"""

from scraper import Configuration
from scraper import news_pool, Source
from tests.conftest import print_test


@print_test
def test_download_works():
    config = Configuration()
    config.memoize_articles = False
    slate_paper = Source('http://slate.com', config=config)
    tc_paper = Source('http://techcrunch.com', config=config)
    espn_paper = Source('http://espn.com', config=config)

    print(('Slate has %d articles TC has %d articles ESPN has %d articles'
           % (slate_paper.size(), tc_paper.size(), espn_paper.size())))

    papers = [slate_paper, tc_paper, espn_paper]
    news_pool.set(papers, threads_per_source=2)

    news_pool.join()

    print('Downloaded Slate mthread len',
          len(slate_paper.articles[0].html))
    print('Downloaded ESPN mthread len',
          len(espn_paper.articles[0].html))
    print('Downloaded TC mthread len',
          len(tc_paper.articles[1].html))
