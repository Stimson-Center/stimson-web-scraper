# -*- coding: utf-8 -*-

import json
import os
from time import time

from scraper import Article, news_pool
from scraper.urls import get_path

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
    articles = [Article(url.replace("\n", "")) for url in urls]
    news_pool.set(articles)
    news_pool.join()
    return articles


def article_curator(test_driver_file):
    print("\n")
    # set variables
    start_time = time()

    # URLPARSE fails on UTF8 string! https://stackoverflow.com/questions/50499273/urlparse-fails-with-simple-url
    with open(test_driver_file,'r', encoding='ascii', errors='ignore') as f:
        urls = [url.replace('\n', '').strip() for url in f if url.replace('\n', '').strip()]

    filedir = os.getenv('HOME')
    # spin up
    articles = article_thread_pool(urls)
    bad_titles = [
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
            if title == '':
                title = get_path(article.url)
                title = title.replace("/", "-")
            elif title.lower() in bad_titles:
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
