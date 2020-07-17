# -*- coding: utf-8 -*-

import json
import os
import pytest

@pytest.mark.options(debug=True)
def test_pdf(fixture_directory, client):
    test_driver_file = os.path.join(fixture_directory, "json", "2015-09-29 Myawaddy industrial zone set for 2017 opening.en.json")
    with open(test_driver_file) as fp:
        payload = fp.read()
    response = client.post("/pdf", json=json.loads(payload))
    assert 200 == response.status_code
    assert '200 OK' == response.status
    assert 'utf-8' == response.charset
    assert response.data
    test_output_file = os.path.join(fixture_directory, "pdf", "2015-09-29 Myawaddy industrial zone set for 2017 opening.en.pdf")
    with open(test_output_file, 'wb') as fp:
        fp.write(response.data)

