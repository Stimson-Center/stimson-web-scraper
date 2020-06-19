# -*- coding: utf-8 -*-
"""
All unit tests for the scraper library should be contained in this file.
"""
import concurrent.futures
import os
import sys
import traceback
import unittest

from scraper import Article
from scraper.urls import get_domain
from tests.conftest import print_test, mock_resource_with

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.abspath(os.path.join(TEST_DIR, '../fixtures'))
URLS_FILE = os.path.abspath(os.path.join(FIXTURES_DIR, 'url/fulltext_list.txt'))


def get_base_domain(url):
    """
    For example, the base url of uk.reuters.com => reuters.com
    """
    domain = get_domain(url)
    tld = '.'.join(domain.split('.')[-2:])
    if tld in ['co.uk', 'com.au', 'au.com']:  # edge cases
        end_chunks = domain.split('.')[-3:]
    else:
        end_chunks = domain.split('.')[-2:]
    base_domain = '.'.join(end_chunks)
    return base_domain


def check_url(*args, **kwargs):
    return ExhaustiveFullTextCase.check_url(*args, **kwargs)


@unittest.skipIf('fulltext' not in sys.argv, 'Skipping fulltext tests')
class ExhaustiveFullTextCase(unittest.TestCase):
    @staticmethod
    def check_url(args):
        """
        :param args:
      """
        url, res_filename = args
        pubdate_failed, fulltext_failed = False, False
        html = mock_resource_with(res_filename, 'html')
        try:
            a = Article(url)
            a.download(html)
            a.parse()
            if a.publish_date is None:
                pubdate_failed = True
                print(f"BAD_PUBDATE={url}")
        except Exception:
            print('<< URL: %s parse ERROR >>' % url)
            traceback.print_exc()
            pubdate_failed, fulltext_failed = True, True
        else:
            correct_text = mock_resource_with(res_filename, 'txt')
            if not (a.text == correct_text):
                # print('Diff: ', simplediff.diff(correct_text, a.text))
                # `correct_text` holds the reason of failure if failure
                print('%s -- %s -- %s' %
                      ('Fulltext failed',
                       res_filename, correct_text.strip()))
                fulltext_failed = True
                # TODO: assert statements are commented out for full-text
                # extraction tests because we are constantly tweaking the
                # algorithm and improving
                # assert a.text == correct_text
        return pubdate_failed, fulltext_failed

    @print_test
    def test_exhaustive(self):
        with open(URLS_FILE, 'r') as f:
            urls = [d.strip() for d in f.readlines() if d.strip()]

        domain_counters = {}

        def get_filename(url):
            domain = get_base_domain(url)
            domain_counters[domain] = domain_counters.get(domain, 0) + 1
            return '{}{}'.format(domain, domain_counters[domain])

        filenames = map(get_filename, urls)

        with concurrent.futures.ProcessPoolExecutor() as executor:
            test_results = list(executor.map(check_url, zip(urls, filenames)))

        total_pubdates_failed, total_fulltext_failed = \
            list(map(sum, zip(*test_results)))

        print('%s fulltext extractions failed out of %s' %
              (total_fulltext_failed, len(urls)))
        print('%s pubdate extractions failed out of %s' %
              (total_pubdates_failed, len(urls)))
        self.assertGreaterEqual(47, total_pubdates_failed)
        self.assertGreaterEqual(38, total_fulltext_failed)


if __name__ == '__main__':
    argv = list(sys.argv)
    if 'fulltext' in argv:
        argv.remove('fulltext')  # remove it here, so it doesn't pass to unittest

    unittest.main(verbosity=0, argv=argv)
