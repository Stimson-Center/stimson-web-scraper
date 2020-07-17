# -*- coding: utf-8 -*-

import json

import pytest

@pytest.mark.options(debug=True)
def test_pdf(client):
    payload = {
        "authors": [
            "Myanmar Times",
            "Bangkok Post Public Company Limited"
        ],
        "config": {
            "language": "en",
            "translate": False
        },
        "html": '<!doctype html>\n<html>\n<head>\n\<\head>"',
        "title": "Myawaddy industrial zone set for 2017 opening",
        "topimage": "https://static.bangkokpost.com/media/content/20150929/c1_711600_700.jpg",
        "url": "https://www.bangkokpost.com/world/711600/myawaddy-industrial-zone-set-for-2017-opening",
        "workflow": [
            "INIT",
            "DOWNLOADED",
            "PARSED",
            "NLPED"
        ],
        "keywords": [
            "zone",
            "myanmar",
            "myawaddy",
            "thailand",
            "electricity",
            "state",
            "factory",
            "naung",
            "mic",
            "industrial",
            "project",
            "kilometres"
        ],
        "images": [
            "https://static.bangkokpost.com/newdesign/assets/images/postgroup-logo_white.svg",
            "https://static.bangkokpost.com/newdesign/assets/images/BangkokPost.svg",
            "https://static.bangkokpost.com/media/content/20150929/c1_711600.jpg",
            "https://static.bangkokpost.com/media/content/20200715/c1_1951928_200715193603.jpg",
            "https://static.bangkokpost.com/media/content/20200715/c1_1951932.jpg",
            "https://static.bangkokpost.com/newdesign/assets/images/BangkokPost-blue.svg",
            "https://static.bangkokpost.com/media/content/20200715/c1_1951936.jpg",
            "https://www.bangkokpost.com/ads/newspaper_direct/enewspaper.jpg?20200716",
            "https://static.bangkokpost.com/media/content/20150929/c1_711600_700.jpg"
        ],
        "language": "en",
        "movies": [],
        "publish_date": "2015-09-29",
        "tables": [],
        "summary": "Myawaddy industrial zone set for 2017 opening",
        "text": "Myawaddy industrial zone set for 2017 opening\n\nThe Mae Sot checkpoint in Tak province is a main trade point ",
        "url": "https://www.bangkokpost.com/world/711600/myawaddy-industrial-zone-set-for-2017-opening"
    }
    response = client.post("/pdf", json=payload)
    assert 200 == response.status_code
    assert '200 OK' == response.status
    assert 'utf-8' == response.charset
    assert response.data

