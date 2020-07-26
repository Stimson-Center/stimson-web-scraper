# -*- coding: utf-8 -*-
"""
Holds misc. utility methods which prove to be
useful throughout this library.
"""

import codecs
import hashlib
import logging
import os
import re
import time

from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parser

from . import settings

__title__ = 'stimson-web-scraper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

TABSSPACE = re.compile(r'[\s\t]+')


class ParsingCandidate(object):

    def __init__(self, url, link_hash):
        self.url = url
        self.link_hash = link_hash


class RawHelper(object):
    @staticmethod
    def get_parsing_candidate(url, raw_html):
        if isinstance(raw_html, str):
            raw_html = raw_html.encode('utf-8', 'replace')
        link_hash = '%s.%s' % (hashlib.md5(raw_html).hexdigest(), time.time())
        return ParsingCandidate(url, link_hash)


class URLHelper(object):
    @staticmethod
    def get_parsing_candidate(url_to_crawl):
        # Replace shebang in urls
        final_url = url_to_crawl.replace('#!', '?_escaped_fragment_=') \
            if '#!' in url_to_crawl else url_to_crawl
        link_hash = '%s.%s' % (hashlib.md5(final_url).hexdigest(), time.time())
        return ParsingCandidate(final_url, link_hash)


class StringSplitter(object):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def split(self, string):
        if not string:
            return []
        return self.pattern.split(string)


class StringReplacement(object):
    def __init__(self, pattern, replaceWith):
        self.pattern = pattern
        self.replaceWith = replaceWith

    def replaceAll(self, string):
        if not string:
            return ''
        return string.replace(self.pattern, self.replaceWith)


class ReplaceSequence(object):
    def __init__(self):
        self.replacements = []

    def create(self, firstPattern, replaceWith=None):
        result = StringReplacement(firstPattern, replaceWith or '')
        self.replacements.append(result)
        return self

    def append(self, pattern, replaceWith=None):
        return self.create(pattern, replaceWith)

    def replaceAll(self, string):
        if not string:
            return ''

        mutatedString = string
        for rp in self.replacements:
            mutatedString = rp.replaceAll(mutatedString)
        return mutatedString


def domain_to_filename(domain):
    """All '/' are turned into '-', no trailing. schema's
    are gone, only the raw domain + ".txt" remains
    """
    filename = domain.replace('/', '-')
    if filename[-1] == '-':
        filename = filename[:-1]
    filename += ".txt"
    return filename

def extract_meta_refresh(html):
    """ Parses html for a tag like:
    <meta http-equiv="refresh" content="0;URL='http://sfbay.craigslist.org/eby/cto/5617800926.html'" />
    Example can be found at: https://www.google.com/url?rct=j&sa=t&url=http://sfbay.craigslist.org/eby/cto/
    5617800926.html&ct=ga&cd=CAAYATIaYTc4ZTgzYjAwOTAwY2M4Yjpjb206ZW46VVM&usg=AFQjCNF7zAl6JPuEsV4PbEzBomJTUpX4Lg
    """
    soup = BeautifulSoup(html, 'lxml')
    element = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if element:
        try:
            wait_part, url_part = element['content'].split(";")
        except ValueError:
            # In case there are not enough values to unpack
            # for instance: <meta http-equiv="refresh" content="600" />
            return None
        else:
            # Get rid of any " or ' inside the element
            # for instance:
            # <meta http-equiv="refresh" content="0;URL='http://sfbay.craigslist.org/eby/cto/5617800926.html'" />
            if url_part.lower().startswith("url="):
                return url_part[4:].replace('"', '').replace("'", '')


def memoize_articles(source, articles):
    """When we parse the <a> links in an <html> page, on the 2nd run
    and later, check the <a> links of previous runs. If they match,
    it means the link must not be an article, because article urls
    change as time passes. This method also uniquifies articles.
    """
    source_domain = source.domain
    config = source.config

    if len(articles) == 0:
        return []

    memo = {}
    cur_articles = {article.url: article for article in articles}
    d_pth = os.path.join(settings.MEMO_DIR, domain_to_filename(source_domain))

    if os.path.exists(d_pth):
        f = codecs.open(d_pth, 'r', 'utf8')
        urls = f.readlines()
        f.close()
        urls = [u.strip() for u in urls]

        memo = {url: True for url in urls}
        # prev_length = len(memo)
        for url, article in list(cur_articles.items()):
            if memo.get(url):
                del cur_articles[url]

        valid_urls = list(memo.keys()) + list(cur_articles.keys())

        memo_text = '\r\n'.join(
            [href.strip() for href in valid_urls])
    # Our first run with memoization, save every url as valid
    else:
        memo_text = '\r\n'.join(
            [href.strip() for href in list(cur_articles.keys())])

    # new_length = len(cur_articles)
    if len(memo) > config.MAX_FILE_MEMO:
        # We still keep current batch of articles though!
        log.critical('memo overflow, dumping')
        memo_text = ''

    # TODO if source: source.write_upload_times(prev_length, new_length)
    ff = codecs.open(d_pth, 'w', 'utf-8')
    ff.write(memo_text)
    ff.close()
    return list(cur_articles.values())


def get_language_codes():
    """Returns a list of available languages and their 2 char input codes
    """
    languages = get_languages()
    two_dig_codes = [k for k, v in languages.items()]
    return two_dig_codes


def get_languages():
    return {
        'af': 'Afrikaans',
        'ar': 'Arabic',
        'bg': 'Bulgarian',
        'bn': 'Bengali',
        'ca': 'Catalan',
        'cs': 'Czech',
        'da': 'Danish',
        'de': 'German',
        'el': 'Greek',
        'en': 'English',
        'es': 'Spanish',
        'et': 'Estonian',
        'eu': 'Basque',
        'fa': 'Persian',
        'fi': 'Finnish',
        'fr': 'French',
        'ga': 'Irish',
        'gu': 'Gujarati',
        'he': 'Hebrew',
        'hi': 'Hindi',
        'hr': 'Croatian',
        'hu': 'Hungarian',
        'hy': 'Armenian',
        'id': 'Indonesian',
        'is': 'Icelandic',
        'it': 'Italian',
        'ja': 'Japanese',
        'kn': 'Kannada',
        'ko': 'Korean',
        'lb': 'Luxembourgish',
        'lij': 'Ligurian',
        'lt': 'Lithuanian',
        'lv': 'Latvian',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'nb': 'Norwegian Bokmål',
        'nl': 'Dutch',
        'pl': 'Polish',
        'pt': 'Portuguese',
        'ro': 'Romanian',
        'ru': 'Russian',
        'si': 'Sinhala',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'sq': 'Albanian',
        'sr': 'Serbian',
        'sv': 'Swedish',
        'ta': 'Tamil',
        'te': 'Telugu',
        'th': 'Thai',
        'tl': 'Tagalog',
        'tr': 'Turkish',
        'tt': 'Tatar',
        'uk': 'Ukrainian',
        'ur': 'Urdu',
        'vi': 'Vietnamese',
        'xx': 'Multi-language',
        'yo': 'Yoruba',
        'zh': 'Chinese'
    }


def extend_config(config, config_items):
    """
    We are handling config value setting like this for a cleaner api.
    Users just need to pass in a named param to this source and we can
    dynamically generate a config object for it.
    """
    for key, val in list(config_items.items()):
        if hasattr(config, key):
            setattr(config, key, val)

    return config


def fulltext(html, language='en'):
    """Takes article HTML string input and outputs the fulltext
    Input string is decoded via UnicodeDammit if needed
    """
    from .document_cleaner import DocumentCleaner
    from .configuration import Configuration
    from .content_extractor import ContentExtractor
    from .output_formatter import OutputFormatter

    config = Configuration()
    config.language = language

    extractor = ContentExtractor(config)
    document_cleaner = DocumentCleaner(config)
    output_formatter = OutputFormatter(config)

    doc = config.get_parser().from_string(html)
    doc = document_cleaner.clean(doc)

    top_node = extractor.calculate_best_node(doc, html)
    if top_node is not None:
        top_node = extractor.post_cleanup(top_node)
        text, article_html = output_formatter.get_formatted(top_node)
    else:
        text = ''
    return text


def parse_date_str(date_str):
    if date_str:
        try:
            return date_parser(date_str)
        except (ValueError, OverflowError, AttributeError, TypeError):
            # near all parse failures are due to URL dates without a day
            # specifier, e.g. /2014/04/
            return None


def innerTrim(value):
    if isinstance(value, str):
        # remove tab and white space
        value = re.sub(TABSSPACE, ' ', value)
        value = ''.join(value.splitlines())
        return value.strip()
    return ''


def split_words(text):
    """Split a string into array of words
    """
    try:
        text = re.sub(r'[^\w ]', '', text)  # strip special chars
        return [x.strip('.').lower() for x in text.split()]
    except TypeError:
        return None

