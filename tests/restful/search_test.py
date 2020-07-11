# -*- coding: utf-8 -*-

import json

import pytest


def validate(response):
    assert 200 == response.status_code
    assert '200 OK' == response.status
    assert 'utf-8' == response.charset
    data = json.loads(response.data)
    return data


# https://pypi.org/project/pytest-flask/
@pytest.mark.options(debug=True)
def test_search_defaults(client):
    payload = {
        "allOfTheseWords": 'tricolor rat terrier',
        "exactTerms": '"rat terrier"',
        "orTerms": 'miniature standard',
        "excludeTerms": 'rodent "Jack Russell"',
        "siteSearch": None,
        "lowRange": "any",
        "highRange": "any",
        "language": "English",
        "country": "United Kingdom",
        "fileType": None,
        "sort": "date",
        "start": 1
    }

    response = client.post("/search", json=payload)
    data = validate(response)
    assert len(data) > 10


# https://pypi.org/project/pytest-flask/
@pytest.mark.options(debug=True)
def test_search_thai(client):
    payload = {
        "allOfTheseWords": "IUU",
        "orTerms": None,
        "country": "Thailand",
        "exactTerms": None,
        "fileType": None,
        "language": "Thai",
        "excludeTerms": None,
        "lowRange": None,
        "highRange": None,
        "start": 1,
        "siteSearch": None,
        "sort": ""
    }

    response = client.post("/search", json=payload)
    data = validate(response)
    assert len(data) > 10  # returned 71 results on 2020/06/10!
