# -*- coding: utf-8 -*-
"""
Wherever smart people work, doors are unlocked. -- Steve Wozniak
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging

from .article import Article, ArticleException
from .configuration import Configuration
from .utils import get_languages, fulltext
from .version import __version__

__title__ = 'stimson-web-scraper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logging.getLogger(__name__).addHandler(NullHandler())
