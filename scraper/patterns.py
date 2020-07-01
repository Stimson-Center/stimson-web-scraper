
import re

# https://www.regextranslator.com/
# http://rick.measham.id.au/paste/explain.pl
# any character                 \w
# any of (letter, digit)        (?:[a-z]|[0-9])
# anything                      .
# at least 3 times              {3,}
# backslash                     \\
# between 3 and 6 times         {3,6}
# capture a                     (a)
# case insensitive              /regex/i
# digit                         \d
# digit from 3 to 5             [3-5]
# either of (digit, letter)     (?:[0-9]|[a-z])
# exactly 3                     {3}
# exactly 4 times               {4}
# letter                        [a-z]
# letter from g to m            [g-m]
# literally "stuff"             (?:stuff)
# multi line                    /regex/m
# must end                      $
# never or more                 *
# new line                      \n
# no character                  \W
# no whitespace                 \S
# no word                       \W
# none of "xyz"                 [^xyz]
# number from 3 to 6            [3-6]
# once                          {1}
# once or more                  +
# one of "defg123"              [defg123]
# optional                      ?
# raw [a-zA-Z]                  [a-zA-Z]
# starts with                   ^
# tab                           \t
# twice                         {2}
# uppercase                     [A-Z]
# uppercase letter from D to Y  [D-Y]
# vertical tab                  \v
# whitespace                    \s
# word                          \b
def get_voltage(sentence):
    pass


# NumberParseException
def get_mobile_number(text):
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),
                       text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number
    return None


def get_email(text):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None



