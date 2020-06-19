# -*- coding: utf-8 -*-
"""
All code involving requests and responses over the http network
must be abstracted in this file.
"""

import logging
import tempfile
from http.cookiejar import CookieJar as cj

import PyPDF4
import pdftotext
import requests
from requests_toolbelt.utils import deprecated

# This site doesn’t like and want scraping. This gives you the same dreaded error 54,
# connection reset by the peer.
from .configuration import Configuration
from .mthreading import ThreadPool

__title__ = 'scraper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'
__maintainer__ = "The Stimson Center"
__maintainer_email = "cooper@pobox.com"

log = logging.getLogger(__name__)

FAIL_ENCODING = 'ISO-8859-1'


def get_request_kwargs(timeout, useragent, proxies, headers):
    """This Wrapper method exists b/c some values in req_kwargs dict
    are methods which need to be called every time we make a request
    """
    return {
        'headers': headers if headers else {'User-Agent': useragent},
        'cookies': cj(),
        'timeout': timeout,
        'allow_redirects': True,
        'proxies': proxies
    }


def get_html(url, config=None, response=None):
    """HTTP response code agnostic
    """
    html, pdf_file_reader = get_html_2XX_only(url, config, response)
    return html, pdf_file_reader


def get_html_2XX_only(url, config=None, response=None):
    """Consolidated logic for http requests from scraper. We handle error cases:
    - Attempt to find encoding of the html by using HTTP header. Fallback to
      'ISO-8859-1' if not provided.
    - Error out if a non 2XX HTTP response code is returned.
    """
    config = config or Configuration()
    useragent = config.browser_user_agent
    timeout = config.request_timeout
    proxies = config.proxies
    headers = config.headers
    pdf_file_reader = None
    pdf_prefix = '%PDF-'

    if response is not None:
        return _get_html_from_response(response, config), pdf_file_reader

    response = requests.get(url=url, **get_request_kwargs(timeout, useragent, proxies, headers))

    html = _get_html_from_response(response, config)

    if response.status_code != 200 and config.http_success_only:
        # fail if HTTP sends a non 2XX response
        response.raise_for_status()

    if html.startswith(pdf_prefix) and html != pdf_prefix:
        html = ""
        pdf_file = tempfile.TemporaryFile(mode='wb+')
        pdf_file.write(response.content)
        pdf_file.flush()
        pdf_file.seek(0)
        pagesAsListOfText = pdftotext.PDF(pdf_file)
        for text in pagesAsListOfText:
            html += text
        pdf_file.seek(0)
        pdf_file_reader = PyPDF4.PdfFileReader(pdf_file)

    return html, pdf_file_reader


def _get_html_from_response(response, config):
    if response.headers.get('content-type') in config.ignored_content_types_defaults:
        return config.ignored_content_types_defaults[response.headers.get('content-type')]
    if response.encoding == FAIL_ENCODING:
        html = response.content
        if 'charset' not in response.headers.get('content-type'):
            # TODO: Cooper, must revisit this hack!
            encodings = deprecated.get_encodings_from_content(response.content)
            if len(encodings) > 0:
                response.encoding = encodings[0]
                html = response.text
    else:
        # return response as a unicode string
        html = response.text

    return html or ''


class MRequest(object):
    """Wrapper for request object for multithreading. If the domain we are
    crawling is under heavy load, the self.resp will be left as None.
    If this is the case, we still want to report the url which has failed
    so (perhaps) we can try again later.
    """

    def __init__(self, url, config=None):
        self.url = url
        self.config = config
        config = config or Configuration()
        self.useragent = config.browser_user_agent
        self.timeout = config.request_timeout
        self.proxies = config.proxies
        self.headers = config.headers
        self.resp = None

    def send(self):
        try:
            self.resp = requests.get(self.url, **get_request_kwargs(
                self.timeout, self.useragent, self.proxies, self.headers))
            if self.config.http_success_only:
                self.resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.critical('[REQUEST FAILED] ' + str(e))


def multithread_request(urls, config=None):
    """Request multiple urls via mthreading, order of urls & requests is stable
    returns same requests but with response variables filled.
    """
    config = config or Configuration()
    num_threads = config.number_threads
    timeout = config.thread_timeout_seconds

    pool = ThreadPool(num_threads, timeout)

    m_requests = []
    for url in urls:
        m_requests.append(MRequest(url, config))

    for req in m_requests:
        pool.add_task(req.send)

    pool.wait_completion()
    return m_requests
