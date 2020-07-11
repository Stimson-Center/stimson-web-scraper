from flask_restful import Resource

from ..constants import languages

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class Languages(Resource):
    @staticmethod
    def get():
        return languages, 200, {'Content-Type': 'application/json'}
