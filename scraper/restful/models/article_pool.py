import random

# https://preslav.me/2019/01/09/dotenv-files-python/
from flask import request
from flask_restful import Resource

from .exporting_thread import ExportingThread

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

exporting_threads = {}


# https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
# https://stackoverflow.com/questions/13279399/how-to-obtain-values-of-request-variables-using-python-and-flask
class ArticlePool(Resource):
    @staticmethod
    def get():
        global exporting_threads
        # print("Args=" + json.dumps(request.args))
        # print("Values=" + json.dumps(request.values))
        # print("Form=" + json.dumps(request.form))
        url = request.args.get('url')
        language = request.args.get('language')
        language = language[:2]
        translate = request.args.get('translate')

        thread_id = random.randint(0, 10000)
        exporting_threads[thread_id] = ExportingThread(url, language=language, translate=translate)
        exporting_threads[thread_id].start()
        result = {"thread_id": thread_id}
        return result, 200, {'Content-Type': 'application/json'}


