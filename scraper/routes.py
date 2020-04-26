#!/usr/bin/env python

import json
import logging

from flask import Flask, request
from scraper import Article
from scraper.configuration import Configuration

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/', methods=['GET'])
def get_article():
    url = request.args.get('url')
    article = _get_article(url)
    return json.dumps({
        "authors": article.authors,
        "html": article.html,
        "images:": list(article.images),
        "keywords": article.keywords,
        "movies": article.movies,
        "publish_date": article.publish_date.strftime("%s") if article.publish_date else None,
        "summary": article.summary,
        "text": article.text,
        "title": article.title,
        "topimage": article.top_image}), 200, {'Content-Type': 'application/json'}


def _get_article(url):
    config = Configuration()
    pdf_defaults = {
        # "application/pdf": "%PDF-",
        # "application/x-pdf": "%PDF-",
        "application/x-bzpdf": "%PDF-",
        "application/x-gzpdf": "%PDF-"
    }
    article = Article(url, request_timeout=config.request_timeout, ignored_content_types_defaults=pdf_defaults)
    article.build()
    # uncomment this if 200 is desired in case of bad url
    # article.set_html(article.html if article.html else '<html></html>')
    return article
