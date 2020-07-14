# https://preslav.me/2019/01/09/dotenv-files-python/
from flask_restful import Resource

from .article_pool import exporting_threads

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


# https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
class ArticleProgress(Resource):
    @staticmethod
    def get(thread_id):
        # print("Args=" + json.dumps(request.args))
        # print("Values=" + json.dumps(request.values))
        # print("Form=" + json.dumps(request.form))
        article = exporting_threads[thread_id].article
        article.get_json()

    @staticmethod
    def delete(thread_id):
        if thread_id in exporting_threads:
            exporting_threads.pop(thread_id)
        return {}, 200, {'Content-Type': 'application/json'}
