# -*- coding: utf-8 -*-
"""
Holds misc. utility methods which prove to be
useful throughout this library.
"""

import codecs
import hashlib
import logging
import os
import pickle
import random
import re
import string
import sys
import threading
import time
import unicodedata
from hashlib import sha1

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parser

from . import settings

__title__ = 'scraper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

TABSSPACE = re.compile(r'[\s\t]+')


class FileHelper(object):
    @staticmethod
    def loadResourceFile(filename):
        if not os.path.isabs(filename):
            dirpath = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(dirpath, 'resources', filename)
        else:
            path = filename
        try:
            f = codecs.open(path, 'r', 'utf-8')
            content = f.read()
            f.close()
            return content
        except IOError:
            raise IOError("Couldn't open file %s" % path)


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


class TimeoutError(Exception):
    pass


def timelimit(timeout):
    """Borrowed from web.py, rip Aaron Swartz
    """

    def _1(function):
        def _2(*args, **kw):
            class Dispatch(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                    self.setDaemon(True)
                    self.start()

                def run(self):
                    # noinspection PyBroadException
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()

            c = Dispatch()
            c.join(timeout)
            if c.is_alive():
                raise TimeoutError()
            if c.error:
                raise c.error[0](c.error[1])
            return c.result

        return _2

    return _1


def domain_to_filename(domain):
    """All '/' are turned into '-', no trailing. schema's
    are gone, only the raw domain + ".txt" remains
    """
    filename = domain.replace('/', '-')
    if filename[-1] == '-':
        filename = filename[:-1]
    filename += ".txt"
    return filename


def filename_to_domain(filename):
    """[:-4] for the .txt at end
    """
    return filename.replace('-', '/')[:-4]


def is_ascii(word):
    """True if a word is only ascii chars
    """

    def onlyascii(char):
        if ord(char) > 127:
            return ''
        else:
            return char

    for c in word:
        if not onlyascii(c):
            return False
    return True


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


def to_valid_filename(s):
    """Converts arbitrary string (for us domain name)
    into a valid file name for caching
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in s if c in valid_chars)


def cache_disk(seconds=(86400 * 5), cache_folder="/tmp"):
    """Caching extracting category locations & rss feeds for 5 days
    """

    def do_cache(function):
        def inner_function(*args, **kwargs):
            """Calculate a cache key based on the decorated method signature
            args[1] indicates the domain of the inputs, we hash on domain!
            """
            key = sha1((str(args[1]) +
                        str(kwargs)).encode('utf-8')).hexdigest()
            filepath = os.path.join(cache_folder, key)

            # verify that the cached object exists and is less than
            # X seconds old
            if os.path.exists(filepath):
                modified = os.path.getmtime(filepath)
                age_seconds = time.time() - modified
                if age_seconds < seconds:
                    return pickle.load(open(filepath, "rb"))

            # call the decorated function...
            result = function(*args, **kwargs)
            # ... and save the cached object for next time
            pickle.dump(result, open(filepath, "wb"))
            return result

        return inner_function

    return do_cache


def print_duration(method):
    """Prints out the runtime duration of a method in seconds
    """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('%r %2.2f sec' % (method.__name__, te - ts))
        return result

    return timed


def chunks(l, n):
    """Yield n successive chunks from l
    """
    newn = int(len(l) / n)
    for i in range(0, n - 1):
        yield l[i * newn:i * newn + newn]
    yield l[n * newn - newn:]


def purge(fn, pattern):
    """Delete files in a dir matching pattern
    """
    for f in os.listdir(fn):
        if re.search(pattern, f):
            os.remove(os.path.join(fn, f))


def clear_memo_cache(source):
    """Clears the memoization cache for this specific news domain
    """
    d_pth = os.path.join(settings.MEMO_DIR, domain_to_filename(source.domain))
    if os.path.exists(d_pth):
        os.remove(d_pth)
    else:
        print('memo file for', source.domain, 'has already been deleted!')


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


def get_useragent():
    """Returns a random useragent in saved file
    """
    with open(settings.USERAGENTS, 'r') as f:
        agents = f.readlines()
        agent = random.choice(agents)
        return agent.strip()


def get_available_language_codes():
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


def get_available_languages():
    """Prints available languages with their full names
    ISO 639-1 Code: https://www.loc.gov/standards/iso639-2/php/code_list.php
    """
    return get_languages()


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


def get_load_time(url):
    # set headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    # make get request to article_url
    response = requests.get(url, headers=headers, stream=True, timeout=10.000)
    # get page load time
    load_time = response.elapsed.total_seconds()
    return load_time


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

    doc = config.get_parser().fromstring(html)
    doc = document_cleaner.clean(doc)

    top_node = extractor.calculate_best_node(doc)
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


def cleanup_text(text):
    """
    It scrubs the garbled from its stream...
    Or it gets the debugger again.
    """
    x = " ".join(map(lambda s: s.strip(), text.split("\n"))).strip()

    x = x.replace('“', '"').replace('”', '"')
    x = x.replace("‘", "'").replace("’", "'").replace("`", "'")
    x = x.replace('…', '...').replace('–', '-')

    x = str(unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('ascii'))

    # some content returns text in bytes rather than as a str ?
    try:
        assert type(x).__name__ == 'str'
    except AssertionError:
        print("not a string?")  # , type(line), line)

    return x


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
