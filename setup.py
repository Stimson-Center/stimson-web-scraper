#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Alan S. Cooper
https://packaging.python.org/tutorials/packaging-projects/
"""

import os
import sys
import setuptools


if sys.argv[-1] == "publish":
    # PYPI now uses twine for package management.
    # For this to work you must first `$ pip3 install twine`
    os.system("python3 setup.py sdist bdist_wheel")
    os.system("python3 -m twine upload dist/*")
    sys.exit()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="stimson-web-scraper",
    version="0.0.21",
    author="Alan S. Cooper",
    author_email="cooper@pobox.com",
    description="website article / adobe pdf file discovery & extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Stimson-Center/stimson-web-scraper",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        scraper=scraper.cli:parse
    ''',
    python_requires=">=3.6",
)
