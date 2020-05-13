#!/bin/python3.7
# -*- coding: utf-8 -*-
"""
Alan S. Cooper
"""

import codecs
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'scraper',
]

if sys.argv[-1] == 'publish':
    # PYPI now uses twine for package management.
    # For this to work you must first `$ pip3 install twine`
    os.system('python3 setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

with open('requirements.txt') as f:
    required = f.read().splitlines()

with codecs.open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='stimson-web-scraper',
    version='0.0.1',
    description='python article / adobe pdf file discovery & extraction.',
    long_description=readme,
    author='Alan S. Cooper',
    author_email='cooper@pobox.com',
    url='https://github.com/praktikos/stimson-web-scraper.git',
    packages=packages,
    include_package_data=True,
    install_requires=required,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
    entry_points='''
        [console_scripts]
        scraper=scraper.cli:parse
    ''',
)
