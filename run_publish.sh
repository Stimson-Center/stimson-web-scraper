#!/usr/bin/env bash

# https://packaging.python.org/tutorials/packaging-projects/
# Twine uploads your project to PyPI from your $HOME/.pypirc file:

if [[ ! -f $HOME/.pypirc ]]
then
    echo "$HOME/.pypirc does not exist on your filesystem."
    exit 1
fi

python3 -m pip install --user --upgrade setuptools wheel twine
[[ -d build ]] && rm -rf build
[[ -d dist ]] && rm -rf dist
pip3 uninstall stimson-web-scraper
python3 setup.py build install publish

# python3 -m twine upload --repository testpypi dist/*
# python3 -m twine upload dist/*
