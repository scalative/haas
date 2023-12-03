#!/usr/bin/env bash
set -ex
export SOURCE_DATE_EPOCH="$(date +%s)"
git clean -fxd
python setup.py sdist
rm -rf build/
python setup.py bdist_wheel --python-tag py3
rm -rf build/
