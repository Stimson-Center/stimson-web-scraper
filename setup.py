#!/bin/python3.7
# -*- coding: utf-8 -*-
"""
Alan S. Cooper
"""

import sys
import os
import codecs


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


# This *must* run early. Please see this API limitation on our users:
# https://github.com/codelucas/newspaper/issues/155
# if sys.version_info[0] == 2 and sys.argv[-1] not in ['publish', 'upload']:
#     sys.exit('WARNING! You are attempting to install stimson-web-scraper\'s '
#              'python3 repository on python2. PLEASE RUN '
#              '`$ pip3 install stimson-web-scraper` for python3'


with open('requirements.txt') as f:
    required = f.read().splitlines()


with codecs.open('README.rst', 'r', 'utf-8') as f:
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
