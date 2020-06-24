# -*- coding: utf-8 -*-
"""
All unit tests for the scraper Article should be contained in this file.
"""
import codecs
import os
import unittest
from collections import defaultdict, OrderedDict

from scraper import Article, fulltext, ArticleException
from scraper.article import ArticleDownloadState
from scraper.configuration import Configuration
from tests.conftest import print_test, mock_resource_with

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.abspath(os.path.join(TEST_DIR, '../fixtures'))
HTML_FN = os.path.abspath(os.path.join(FIXTURES_DIR, 'html'))


class ArticleTestCase(unittest.TestCase):
    def setup_stage(self, stage_name):
        stages = OrderedDict([
            ('initial', lambda: None),
            ('download', lambda: self.article.download(
                mock_resource_with('cnn_article', 'html'))),
            ('parse', lambda: self.article.parse()),
            ('meta', lambda: None),  # Alias for nlp
            ('nlp', lambda: self.article.nlp())
        ])
        assert stage_name in stages
        for name, action in stages.items():
            if name == stage_name:
                break
            action()

    def setUp(self):
        """Called before the first test case of this unit begins
        """
        self.article = Article(
            url='http://www.cnn.com/2013/11/27/travel/weather-thanksgiving/index.html?iref=allsearch')

    @print_test
    def test_url(self):
        self.assertEqual(
            'http://www.cnn.com/2013/11/27/travel/weather-thanksgiving/index.html?iref=allsearch',
            self.article.url)

    @print_test
    def test_download_html(self):
        self.setup_stage('download')
        html = mock_resource_with('cnn_article', 'html')
        self.article.download(html)
        self.assertEqual(self.article.download_state, ArticleDownloadState.SUCCESS)
        self.assertEqual(self.article.download_exception_msg, None)
        self.assertEqual(75406, len(self.article.html))

    @print_test
    def test_meta_refresh_redirect(self):
        # TODO: We actually hit example.com in this unit test ... which is bad
        # Figure out how to mock an actual redirect
        config = Configuration()
        config.follow_meta_refresh = True
        article = Article('', config=config)
        html = mock_resource_with('google_meta_refresh', 'html')
        article.download(input_html=html)
        article.parse()
        self.assertEqual(article.title, 'Example Domain')

    @print_test
    def test_meta_refresh_no_url_redirect(self):
        config = Configuration()
        config.follow_meta_refresh = True
        article = Article(
            '', config=config)
        html = mock_resource_with('ap_meta_refresh', 'html')
        article.download(input_html=html)
        article.parse()
        self.assertEqual(article.title, 'News from The Associated Press')

    @print_test
    def test_pre_download_parse(self):
        """Calling `parse()` before `download()` should yield an error
        """
        article = Article(self.article.url)
        self.assertRaises(ArticleException, article.parse)

    @print_test
    def test_parse_html(self):
        self.setup_stage('parse')

        AUTHORS = ['Chien-Ming Wang', 'Dana A. Ford', 'James S.A. Corey',
                   'Tom Watkins']
        TITLE = 'After storm, forecasters see smooth sailing for Thanksgiving'
        LEN_IMGS = 46
        META_LANG = 'en'
        META_SITE_NAME = 'CNN'

        self.article.parse()
        self.article.nlp()

        text = mock_resource_with('cnn', 'txt')
        self.maxDiff=None
        self.assertEqual(text.strip(), self.article.text)
        self.assertEqual(text, fulltext(self.article.html))

        # NOTE: top_img extraction requires an internet connection
        # unlike the rest of this test file
        TOP_IMG = ('http://i2.cdn.turner.com/cnn/dam/assets/131129200805-'
                   '01-weather-1128-story-top.jpg')
        self.assertEqual(TOP_IMG, self.article.top_img)

        self.assertCountEqual(AUTHORS, self.article.authors)
        self.assertEqual(TITLE, self.article.title)
        self.assertEqual(LEN_IMGS, len(self.article.imgs))
        self.assertEqual(META_LANG, self.article.meta_lang)
        self.assertEqual(META_SITE_NAME, self.article.meta_site_name)
        self.assertEqual('2013-11-27', str(self.article.publish_date))

    @print_test
    def test_meta_type_extraction(self):
        self.setup_stage('meta')
        meta_type = self.article.extractor.get_meta_type(
            self.article.clean_doc)
        self.assertEqual('article', meta_type)

    @print_test
    def test_meta_extraction(self):
        self.setup_stage('meta')
        meta = self.article.extractor.get_meta_data(self.article.clean_doc)
        META_DATA = defaultdict(dict, {
            'medium': 'news',
            'googlebot': 'noarchive',
            'pubdate': '2013-11-27T08:36:32Z',
            'title': 'After storm, forecasters see smooth sailing for Thanksgiving - CNN.com',
            'og': {'site_name': 'CNN',
                   'description': 'A strong storm struck much of the eastern United States on Wednesday, complicating holiday plans for many of the 43 million Americans expected to travel.',
                   'title': 'After storm, forecasters see smooth sailing for Thanksgiving',
                   'url': 'http://www.cnn.com/2013/11/27/travel/weather-thanksgiving/index.html',
                   'image': 'http://i2.cdn.turner.com/cnn/dam/assets/131129200805-01-weather-1128-story-top.jpg',
                   'type': 'article'},
            'section': 'travel',
            'author': 'Dana A. Ford, James S.A. Corey, Chien-Ming Wang, and Tom Watkins, CNN',
            'robots': 'index,follow',
            'vr': {
                'canonical': 'http://edition.cnn.com/2013/11/27/travel/weather-thanksgiving/index.html'},
            'source': 'CNN',
            'fb': {'page_id': 18793419640, 'app_id': 80401312489},
            'keywords': 'winter storm,holiday travel,Thanksgiving storm,Thanksgiving winter storm',
            'article': {
                'publisher': 'https://www.facebook.com/cnninternational'},
            'lastmod': '2013-11-28T02:03:23Z',
            'twitter': {'site': {'identifier': '@CNNI', 'id': 2097571},
                        'card': 'summary',
                        'creator': {'identifier': '@cnntravel',
                                    'id': 174377718}},
            'viewport': 'width=1024',
            'news_keywords': 'winter storm,holiday travel,Thanksgiving storm,Thanksgiving winter storm'
        })

        self.assertDictEqual(META_DATA, meta)

        # if the value for a meta key is another dict, that dict ought to be
        # filled with keys and values
        dict_values = [v for v in list(meta.values()) if isinstance(v, dict)]
        self.assertTrue(all([len(d) > 0 for d in dict_values]))

        # there are exactly 5 top-level "og:type" type keys
        is_dict = lambda v: isinstance(v, dict)
        self.assertEqual(5, len([i for i in meta.values() if is_dict(i)]))

        # there are exactly 12 top-level "pubdate" type keys
        is_string = lambda v: isinstance(v, str)
        self.assertEqual(12, len([i for i in meta.values() if is_string(i)]))

    @print_test
    def test_pre_download_nlp(self):
        """Test running NLP algos before even downloading the article
        """
        self.setup_stage('initial')
        new_article = Article(self.article.url)
        self.assertRaises(ArticleException, new_article.nlp)

    @print_test
    def test_pre_parse_nlp(self):
        """Test running NLP algos before parsing the article
        """
        self.setup_stage('parse')
        self.assertRaises(ArticleException, self.article.nlp)

    @print_test
    def test_nlp_body(self):
        self.setup_stage('nlp')
        self.article.nlp()
        KEYWORDS = [
            'weather',
            'storm',
            'New',
            'balloons',
            'York',
            'flight',
            'Thanksgiving',
            'roads',
            'delays',
            'people',
            'winds',
            'parade'
        ]
        self.assertCountEqual(KEYWORDS, self.article.keywords)
        SUMMARY = mock_resource_with('cnn_summary', 'txt')
        self.assertEqual(SUMMARY, self.article.summary)

    @print_test
    def test_download_file_success(self):
        url = "file://" + os.path.join(HTML_FN, "cnn_article.html")
        article = Article(url=url)
        article.download()
        self.assertEqual(article.download_state, ArticleDownloadState.SUCCESS)
        self.assertEqual(article.download_exception_msg, None)
        self.assertEqual(75406, len(article.html))

    @print_test
    def test_download_file_failure(self):
        url = "file://" + os.path.join(HTML_FN, "does_not_exist.html")
        article = Article(url=url)
        article.download()
        self.assertEqual(0, len(article.html))
        self.assertEqual(article.download_state, ArticleDownloadState.FAILED_RESPONSE)
        self.assertEqual(article.download_exception_msg, "No such file or directory")

    @print_test
    def test_wikipedia_tables(self):
        url = "https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart_for_English_dialects"
        article = Article(url=url)
        article.build()
        self.assertEqual(article.download_state, ArticleDownloadState.SUCCESS)
        self.assertEqual(article.download_exception_msg, None)
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
