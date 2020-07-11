import logging
import threading

# https://preslav.me/2019/01/09/dotenv-files-python/
# noinspection PyPackageRequirements
from scraper import Article
# noinspection PyPackageRequirements
from scraper.configuration import Configuration

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

exporting_threads = {}
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class ExportingThread(threading.Thread):
    def __init__(self, url, language='en', translate=False):
        self.progress = 0
        config = Configuration()
        config.follow_meta_refresh = True
        config.use_meta_language = False
        config.set_language(language)
        if isinstance(translate, str):
            translate = translate.lower() == 'true'
        config.translate = translate
        config.http_success_only = False
        config.ignored_content_types_defaults = {
            # "application/pdf": "%PDF-",
            # "application/x-pdf": "%PDF-",
            "application/x-bzpdf": "%PDF-",
            "application/x-gzpdf": "%PDF-"
        }
        # print(f"translate={translate}")
        self.article = Article(url, config=config)
        super().__init__()

    def run(self):
        # Your exporting stuff goes here ...
        self.progress = 20
        self.article.download()
        self.progress = 40
        # uncomment this if 200 is desired in case of bad url
        # self.article.set_html(article.html if article.html else '<html></html>')
        self.article.parse()
        self.progress = 60
        self.article.nlp()
        self.progress = 100
