# -*- coding: utf-8 -*-

import json
import os
from time import time
import datetime
from futures3 import ThreadPoolExecutor, as_completed

from scraper import ArticleExecutor
from scraper.urls import b64_encode


def save_article(article, filename, filedir='/tmp'):
    a = {
        'title': article.title,
        'authors': article.authors,
        'publish_date': article.publish_date,
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


def article_thread_pool(urls):
    articles = []
    # https://docs.python.org/3/library/concurrent.futures.html
    max_worker_threads = 20
    # We can use a with statement to ensure threads are cleaned up promptly
    with ThreadPoolExecutor(max_workers=max_worker_threads) as executor:
        # Start the load operations and mark each future with its URL
        future_to_article = {executor.submit(ArticleExecutor, url): url for url in urls}
        for future in as_completed(future_to_article):
            try:
                articles.append(future.result())
            except Exception as exc:
                # print('%r generated an exception: %s' % (a42_wo_wordorder, exc))
                print(exc)
    return articles


def article_curator(test_driver_file):
    print("\n")
    # set variables
    start_time = time()

    with open(test_driver_file, encoding='utf-8') as f:
        urls = [url for url in f]

    filedir = os.getenv('HOME')
    articles = article_thread_pool(urls)
    bad_titles = [
        "",
        "404 not found",
        "404",
        "503 service temporarily unavailable",
        "522/ connection timed out",
        "not found",
        "access denied",
        "server connection terminated",
        "page not found",
        "sorry, the page you were looking for was not found",
        "page not found - the australian-thai chamber of commerce (austcham)"
    ]
    for article in articles:
        try:
            title = article.title if article.title else ''
            title = title.replace("/", " ").replace("\\", " ").strip()
            if title == '' or title.lower() in bad_titles:
                print(f"Error: {title} {article.url}")
                continue
            publish_date = article.publish_date[0:10].strip() if article.publish_date else ''
            article.publish_date = publish_date
            if publish_date:
                filename = f'{publish_date} {title}.json'
            else:
                filename = f'{title}.json'
            # encoded = b64_encode(article.url)
            # filename = encoded + '.json'
            # # filename = article.link_hash + '.json'
            save_article(article, filename, filedir=filedir)
        except Exception as exc:
            print('%r generated an exception: %s' % (article.url, exc))

    total_elapsed_time = time() - start_time
    print(f'Total elapsed time {total_elapsed_time} seconds')


# noinspection PyUnresolvedReferences
def test_industrial_spaces_urls(fixture_directory):
    test_driver_file = os.path.join(fixture_directory, "energy_investment_mekong_delta", "industrial_spaces_url.txt")
    article_curator(test_driver_file)


# noinspection PyUnresolvedReferences
def test_illegal_unreported_and_unregulated_fishing_urls(fixture_directory):
    test_driver_file = os.path.join(fixture_directory, "illegal-unreported-and-unregulated-fishing", "urls.txt")
    article_curator(test_driver_file)


# noinspection PyUnresolvedReferences
def test_energy_investment_mekong_delta_urls(fixture_directory):
    test_driver_file = os.path.join(fixture_directory, "energy_investment_mekong_delta", "Thailand.url")
    article_curator(test_driver_file)
