set -ex
export SOURCE_DATE_EPOCH="$(date +%s)"
git clean -fxd
python setup.py sdist
rm -rf build/
python setup.py bdist_wheel --python-tag py26
rm -rf build/
python setup.py bdist_wheel --python-tag py27.py32.py33
rm -rf build/
python setup.py bdist_wheel --python-tag py34
rm -rf build/
