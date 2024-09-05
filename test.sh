#!/bin/bash
cd $(cd $(dirname $0) && pwd)

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf >/dev/null 2>&1
test -d build && rm -r build
test -d dist && rm -r dist
test -d *.egg-info && rm -r *.egg-info
python3 setup.py clean

docker build -f Dockerfile_dev --build-arg BUILD_NO=$RANDOM -t fastflyer:dev .
docker run \
    --rm -ti \
    --net host \
    -e flyer_port=8889 \
    -e flyer_zhiyan_log_enabled=1 \
    -e flyer_zhiyan_log_proto=dev \
    -e flyer_zhiyan_log_topic=sdk-d1egacb2gg5e87ea \
    -e flyer_access_log=1 \
    -v $(pwd):/fastflyer \
    fastflyer:dev \
