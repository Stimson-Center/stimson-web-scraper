#!/usr/bin/env python3


import click
import json
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

# noinspection PyPep8
from scraper import Article
# noinspection PyPep8
from scraper.utils import get_available_language_codes


@click.command()
@click.option('--language', '-l', default='en', help='Language in which the text is written',
              type=click.Choice(get_available_language_codes()))
@click.option('--url', '-u', help='URL to parse', required=True)
def parse(url, language):
    article = Article(url, language=language)
    article.build()
    if article.keywords:
        print('Article Keywords: ' + json.dumps(article.keywords) + '\n')
    if article.summary:
        print('Article Summary: ' + article.summary + '\n')
    print('Article Text: ' + article.text)


if __name__ == '__main__':
    parse()

#
# import datetime
# import json
# from itertools import repeat
# from multiprocessing import Pool, cpu_count
# from time import sleep, time
#
# from scraper.google_customsearch import GoogleCustomSearch
# from scraper.news_ycombinator import connect_to_base, parse_html, write_to_file
# from scraper.chromium import get_driver
#
#
# def run_process(page_number, output_filename):
#     browser = get_driver()
#     if connect_to_base(browser, page_number):
#         sleep(2)
#         html = browser.page_source
#         output_list = parse_html(html)
#         write_to_file(output_list, output_filename)
#     else:
#         print('Error connecting to hackernews')
#     browser.quit()
#
#
# def run_google_scholar_search():
#     google_search = GoogleCustomSearch()
#     google_search_urls = google_search.get_search_urls("child AND soldiers", 10)
#     print(json.dumps(google_search_urls, sort_keys=True, indent=4))
#     scholar_sites = google_search.get_scholar_list(google_search_urls)
#     print(json.dumps(scholar_sites, sort_keys=True, indent=4))
#
#
# if __name__ == '__main__':
#     # set variables
#     start_time = time()
#     output_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
#     output_filename = f'output_{output_timestamp}.csv'
#     # scrape and crawl
#     with Pool(cpu_count() - 1) as p:
#         p.starmap(run_process, zip(range(1, 21), repeat(output_filename)))
#     p.close()
#     p.join()
#     end_time = time()
#     elapsed_time = end_time - start_time
#     print(f'Elapsed run time: {elapsed_time} seconds')
