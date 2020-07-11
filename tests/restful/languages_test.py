# -*- coding: utf-8 -*-

import json

import pytest


# https://pypi.org/project/pytest-flask/
@pytest.mark.options(debug=True)
def test_languages(client):
    response = client.get("/languages")
    assert 200 == response.status_code
    assert '200 OK' == response.status
    assert 'utf-8' == response.charset
    data = json.loads(response.data)
    assert len(data) == 83
    assert data['English'] == 'en'
