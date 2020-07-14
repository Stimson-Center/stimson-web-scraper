# -*- coding: utf-8 -*-
"""
All unit tests for the scraper public API should be contained in this file.
"""

from scraper.patterns import get_voltage, get_email, get_mobile_number
from tests.conftest import print_test

# https://www.power-technology.com/projects/dai-nanh/

@print_test
def test_get_voltage():
    sentence = 'The 300MW Dai Ninh hydroelectric plant in Vietnam was commissioned in March 2008'
    voltage = get_voltage(sentence)
    # assert voltage
    pass


@print_test
def test_get_mobile_number():
    sentence = "Alan Cooper\nemail:\tcooper@pobox.com\nmobile:+1555.555.5555"
    mobile = get_mobile_number(sentence)
    assert mobile
    assert mobile == "+15555555555"

@print_test
def test_get_email():
    sentence = "Alan Cooper\nemail:\tcooper@pobox.com\nmobile:+1555.555.5555"
    email = get_email(sentence)
    assert email
    assert email == "cooper@pobox.com"
