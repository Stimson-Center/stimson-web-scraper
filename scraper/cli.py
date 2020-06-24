#!/usr/bin/env python3


import json
import os
import sys

import click

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
