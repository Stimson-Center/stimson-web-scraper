# -*- coding: utf-8 -*-

import json

import pytest


# https://pypi.org/project/pytest-flask/
@pytest.mark.options(debug=True)
def test_countries(client):
    response = client.get("/countries")
    assert 200 == response.status_code
    assert '200 OK' == response.status
    assert 'utf-8' == response.charset
    data = json.loads(response.data)
    assert len(data) == 242
    assert data["United States"] == "countryUS"
