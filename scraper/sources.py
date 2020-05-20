#!/usr/bin/env python3


from . import urls
# noinspection PyPackageRequirements
from .article import Article
from .source import Source

__title__ = 'scraper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class Sources:
    def __init__(self, url, language='en'):
        self.url = urls.prepare_url(url)
        self.language = language
        self.source = Source(self.url, language=language)
        self.source.download()
        self.source.parse()
        self.source.set_categories()
        self.source.download_categories()  # mthread
        self.source.parse_categories()
        self.source.generate_articles()
        self.article = Article(self.url, language=self.language)

    def get_articles(self):
        # type: () -> list
        return self.source.article_urls()

    def get_categories(self):
        # type: () -> list
        return self.source.category_urls()

    def build(self):
        # type: () -> None
        self.article.build()
