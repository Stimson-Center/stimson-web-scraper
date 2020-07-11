import logging
import os
import time

import pytest
from flask import Flask
from flask_restful import Api

from scraper.restful.endpoints import create_routes, get_cors


# noinspection PyProtectedMember
@pytest.fixture
def fixture_directory():
    return os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(scope='function')
def app():
    app = Flask("test")
    api = Api(app)
    create_routes(api)
    app.logger.setLevel(logging.DEBUG)
    cors = get_cors(app)
    return app


def mock_resource_with(filename, resource_type):
    """
    Mocks an HTTP request by pulling text from a pre-downloaded file
    """
    VALID_RESOURCES = ['html', 'txt']
    if resource_type not in VALID_RESOURCES:
        raise Exception('Mocked resource must be one of: %s' %
                        ', '.join(VALID_RESOURCES))
    subfolder = 'text' if resource_type == 'txt' else 'html'
    FIXTURE_DIRECTORY = os.path.join(os.path.dirname(__file__), "fixtures")
    resource_path = os.path.join(FIXTURE_DIRECTORY, "%s/%s.%s" %
                                 (subfolder, filename, resource_type))
    with open(resource_path, 'r', encoding='utf-8') as f:
        return f.read()


def print_test(method):
    """
    Utility method for print verbalizing test suite, prints out
    time taken for test and functions name, and status
    """

    def run(*args, **kw):
        ts = time.time()
        print('\ttesting function %r' % method.__name__)
        method(*args, **kw)
        te = time.time()
        print('\t[OK] in %r %2.2f sec' % (method.__name__, te - ts))

    return run
