# from .endpoints import user  # noqa

import logging

# https://preslav.me/2019/01/09/dotenv-files-python/
from flask_cors import CORS
from flask_restful import Resource

from .models import *

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def get_cors(app):
    # https://github.com/corydolphin/flask-cors/issues/201
    cors = CORS(app,
                resources={r"/*": {"origins": "*"}},
                origins=f"http://127.0.0.1:{5000}",
                allow_headers=[
                    "Content-Type", "Authorization",
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Credentials"],
                supports_credentials=True
                )
    return cors

# @app.before_request
# def authorize_token():
#     pass
#     # if request.endpoint != 'token':
#     #     try:
#     #         auth_header = request.headers.get("Authorization")
#     #         if "Bearer" in auth_header:
#     #             token = auth_header.split(' ')[1]
#     #             if token != '12345678':
#     #                 raise ValueError('Authorization failed.')
#     #     except Exception as e:
#     #         return "401 Unauthorized\n{}\n\n".format(e), 401


class GetToken(Resource):
    @staticmethod
    def post():
        token = '12345678'
        return token  # token sent to client to return in subsequent
        # requests in Authorization header


def create_routes(api):
    api.add_resource(HelloWorld, '/')
    api.add_resource(ArticlePool, '/article')
    api.add_resource(ArticleProgress, '/article/<int:thread_id>')
    api.add_resource(Countries, '/countries')
    api.add_resource(FileTypes, '/filetypes')
    api.add_resource(Languages, '/languages')
    api.add_resource(Search, '/search')
    api.add_resource(Share, '/share')
