# -*- coding: utf-8 -*-

import json

import pytest


# https://pypi.org/project/pytest-flask/

@pytest.mark.options(debug=False)
def test_app(app):
    assert not app.debug, 'Ensure the app not in debug mode'


@pytest.mark.options(debug=True)
def test_health(client):
    response = client.get("/")
    assert 200 == response.status_code
    assert '200 OK' == response.status
    assert 'utf-8' == response.charset
    data = json.loads(response.data)
    assert 0 < data['cpu_in_use'] < 100
    assert 0 < data['memory_in_use'] < 100
    assert 0 < data['diskspace_in_use'] < 100
