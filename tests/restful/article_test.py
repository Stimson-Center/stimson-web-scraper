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
def test_article_yahoo(client):
    response1 = client.get("/article?url=https://www.yahoo.com&language=en&translate=false")
    response1_data = validate(response1)
    assert len(response1_data) == 15  # returned 15 results on 2020/07/13!
    progress = response1_data['progress']
    while progress < 100:
        response2 = client.get("/article/" + str(response1_data['thread_id']))
        response2_data = validate(response2)
        assert len(response2_data) == 15  # returned 15 results on 2020/07/13!
        progress = response2_data['progress']
        pass
    assert len(response2_data['text'])

