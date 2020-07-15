# https://preslav.me/2019/01/09/dotenv-files-python/
from flask import request
from flask_restful import Resource

# https://preslav.me/2019/01/09/dotenv-files-python/
# noinspection PyPackageRequirements
from scraper import Article
from scraper.article import DOWNLOADED, PARSED, NLPED
# noinspection PyPackageRequirements
from scraper.configuration import Configuration

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class ArticleProcess(Resource):
    @staticmethod
    def get():
        # print("Args=" + json.dumps(request.args))
        # print("Values=" + json.dumps(request.values))
        # print("Form=" + json.dumps(request.form))
        url = request.args.get('url')
        language = request.args.get('language')
        language = language[:2]
        translate = request.args.get('translate')
        article = ArticleProcess.create_article(url, language, translate)
        return article.get_json(), 200, {'Content-Type': 'application/json'}

    @staticmethod
    def post():
        form = request.get_json()
        article = ArticleProcess.create_article(form['url'], form['config']['language'], form['config']['translate'])
        article.set_json(form)
        if DOWNLOADED not in article.workflow:
            article.download()
        elif PARSED not in article.workflow:
            article.parse()
        elif NLPED not in article.workflow:
            article.nlp()
        return article.get_json(), 200, {'Content-Type': 'application/json'}

    @staticmethod
    def create_article(url, language, translate):
        config = Configuration()
        # initialization runtime configuration
        config.follow_meta_refresh = True
        config.use_meta_language = False
        config.set_language(language)
        if isinstance(translate, str):
            translate = translate.lower() == 'true'
        config.set_translate(translate)
        config.http_success_only = False
        config.ignored_content_types_defaults = {
            # "application/pdf": "%PDF-",
            # "application/x-pdf": "%PDF-",
            "application/x-bzpdf": "%PDF-",
            "application/x-gzpdf": "%PDF-"
        }
        return Article(url, config=config)
