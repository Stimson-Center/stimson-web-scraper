import json
import os

# https://preslav.me/2019/01/09/dotenv-files-python/
from dotenv import load_dotenv
from flask import request
from flask_restful import Resource

from scraper.restful.utils import valid_filename

__title__ = 'stimson-web-scraper'
__author__ = 'Alan S. Cooper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020, The Stimson Center'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"


class Share(Resource):
    @staticmethod
    def post():
        # https://codelabs.developers.google.com/codelabs/gsuite-apis-intro/#0
        # Get environment variables
        load_dotenv()
        # api_key = os.getenv('GOOGLE_SECRET_API_KEY')
        # cse_id = os.getenv('GOOGLE_SECRET_CUSTOM_SEARCH_ID')
        home = os.getenv('HOME')
        form = request.get_json()
        form.pop('progress', None)
        form.pop('thread_id', None)
        publish_date = form['publish_date'][0:10] if form['publish_date'] else ''
        title = valid_filename(form['title'])
        filename = f"{publish_date} {title}"
        # Save json to file, filename length <=255
        # https://stackoverflow.com/questions/265769/maximum-filename-length-in-ntfs-windows-xp-and-windows-vista#:~:text=14%20Answers&text=Individual%20components%20of%20a%20filename,files%2C%20248%20for%20folders).
        filepath = os.path.join(home, filename[0:230] + ".json")
        # noinspection PyUnusedLocal
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(json.dumps(form, indent=4, sort_keys=True))
        return {"filepath": filepath}, 200, {'Content-Type': 'application/json'}
