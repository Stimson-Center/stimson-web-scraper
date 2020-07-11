from flask_restful import Resource

from ..constants import file_types

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class FileTypes(Resource):
    @staticmethod
    def get():
        return file_types, 200, {'Content-Type': 'application/json'}
