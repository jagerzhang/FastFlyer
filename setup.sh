#!/bin/bash
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf >/dev/null 2>&1

test -d build && rm -r build
test -d dist && rm -r dist
test -d *.egg-info && rm -r *.egg-info

python3 setup.py clean
python3 setup.py sdist
# python3 setup.py install

if [[ $publish -eq 1 ]];then
    twine upload dist/*.tar.gz
fi

test -d build && rm -r build
test -d dist && rm -r dist
test -d *.egg-info && rm -r *.egg-info
