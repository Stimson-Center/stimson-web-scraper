# -*- coding: utf-8 -*-

import json
import os
from time import time

from scraper.urls import b64_encode
from scraper import ArticlePool


def save_article(article, filename, filedir='/tmp'):
    a = {
        'title': article.title,
        'authors': article.authors,
        'publish_date': str(article.publish_date),
        'summary': article.summary,
        'keywords': article.keywords,
        'text': article.text,
        'url': article.url,
        'tables': article.tables
    }
    filepath = os.path.join(filedir, filename)
    # noinspection PyUnusedLocal
    try:
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(json.dumps(a, indent=4, sort_keys=True))
    except Exception as ex:
        pass


# noinspection PyUnresolvedReferences
def test_illegal_unreported_and_unregulated_fishing_urls(fixture_directory):
    test_driver_file = os.path.join(fixture_directory, "illegal-unreported-and-unregulated-fishing", "urls.txt")
    print("\n")
    # set variables
    start_time = time()

    with open(test_driver_file, encoding='utf-8') as f:
        urls = [url for url in f]

    article_pool = ArticlePool()
    articles = article_pool.run(urls)
    for article in articles:
        try:
            encoded = b64_encode(article.url)
            filename = encoded + '.json'
            # # filename = article.link_hash + '.json'
            save_article(article, filename, filedir='/tmp')
        except Exception as exc:
            print('%r generated an exception: %s' % (article.url, exc))

    total_elapsed_time = time() - start_time
    print(f'Total elapsed time {total_elapsed_time} seconds')
