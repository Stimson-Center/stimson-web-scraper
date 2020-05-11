# -*- coding: utf-8 -*-

import json
import os
from time import time

from scraper import Article
from scraper.urls import b64_encode
from scraper import news_pool
from scraper.configuration import Configuration


def save_article(article, filename, filedir='/tmp'):
    a = {
        'title': article.title,
        'authors': article.authors,
        'publish_date': str(article.publish_date),
        'summary': article.summary,
        'keywords': article.keywords,
        'text': article.text,
        'url': article.url
    }
    filepath = os.path.join(filedir, filename)
    # noinspection PyUnusedLocal
    try:
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(json.dumps(a, indent=4, sort_keys=True))
    except Exception as ex:
        pass


# noinspection PyUnresolvedReferences
def test_b64_encode(fixture_directory):
    test_driver_file = os.path.join(fixture_directory, "energy_investment_mekong_delta", "Thailand.url")
    with open(test_driver_file, encoding='utf-8') as f:
        for line in f:
            url = line.rstrip()
            filename = b64_encode(url)
            assert filename


# noinspection PyUnresolvedReferences
def test_get_mekong_delta_urls(fixture_directory):
    test_driver_file = os.path.join(fixture_directory, "energy_investment_mekong_delta", "Thailand.url")
    websites = list()
    config = Configuration()
    config.memoize_articles = False
    pdf_defaults = {
        # "application/pdf": "%PDF-",
        # "application/x-pdf": "%PDF-",
        "application/x-bzpdf": "%PDF-",
        "application/x-gzpdf": "%PDF-"
    }
    print("\n")
    # set variables
    total_start_time = time()
    with open(test_driver_file, encoding='utf-8') as f:
        build_start_time = time()
        for line in f:
            # scrape and crawl
            # websites.append(scraper.build(line.rstrip(), config=config))
            websites.append(Article(line.rstrip(), request_timeout=config.request_timeout,
                                    ignored_content_types_defaults=pdf_defaults))
            # break # only process the first url in file

        build_end_time = time()
        build_elapsed_time = build_end_time - build_start_time
        print(f'Build elapsed time {build_elapsed_time} seconds')

    download_start_time = time()
    news_pool.set(websites, threads_per_source=2)
    news_pool.join()
    download_end_time = time()
    download_elapsed_time = download_end_time - download_start_time
    print(f'Download elapsed time {download_elapsed_time} seconds')

    persist_start_time = time()
    for article in websites:
        encoded = b64_encode(article.url)
        filename = encoded + '.json'
        # # filename = article.link_hash + '.json'
        save_article(article, filename, filedir='/tmp')
    persist_end_time = time()
    persist_elapsed_time = persist_end_time - persist_start_time
    print(f'Persist elapsed time {persist_elapsed_time} seconds')

    total_end_time = time()
    total_elapsed_time = total_end_time - total_start_time
    print(f'Total elapsed time {total_elapsed_time} seconds')


def test_wikipedia():
    import codecs
    url = "https://en.wikipedia.org/wiki/List_of_power_stations_in_Vietnam"
    article = Article(url=url)
    article.build()

    # write data out to tab seperated format
    page = os.path.split(url)[1]
    for table in article.tables:
        fname = '../{}_t{}.tsv'.format(page, table['name'])
        with codecs.open(fname, 'w') as f:
            for i in range(len(table['rows'])):
                rowStr = '\t'.join(table['rows'][i])
                rowStr = rowStr.replace('\n', '')
                # print(rowStr)
                f.write(rowStr + '\n')
            f.close()
