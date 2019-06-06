#!/usr/bin/env bash

pip3 install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel

pip3 install --user --upgrade twine
twine upload dist/*
