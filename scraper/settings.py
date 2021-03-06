# -*- coding: utf-8 -*-
"""
Unlike configuration.py, this file is meant for static, entire project
encompassing settings, like memoization and caching file directories.
"""

import logging
import os
import tempfile

from .version import __version__

__title__ = 'stimson-web-scraper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

log = logging.getLogger(__name__)

PARENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

DATA_DIRECTORY = '.scraper'

TOP_DIRECTORY = os.path.join(tempfile.gettempdir(), DATA_DIRECTORY)

# Error log
LOGFILE = os.path.join(TOP_DIRECTORY, 'newspaper_errors_%s.log' % __version__)
MONITOR_LOGFILE = os.path.join(
    TOP_DIRECTORY, 'newspaper_monitors_%s.log' % __version__)

# Memo directory (same for all concur crawlers)
MEMO_FILE = 'memoized'
MEMO_DIR = os.path.join(TOP_DIRECTORY, MEMO_FILE)

# category and feed cache
CF_CACHE_DIRECTORY = 'feed_category_cache'
ANCHOR_DIRECTORY = os.path.join(TOP_DIRECTORY, CF_CACHE_DIRECTORY)

for path in (TOP_DIRECTORY, MEMO_DIR, ANCHOR_DIRECTORY):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
