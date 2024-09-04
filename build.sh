#!/bin/bash
docker build --build-arg BUILD_NO=$(date +%s) -t mirrors.tencent.com/nops/fastflyer:latest ./ && \
docker push mirrors.tencent.com/nops/fastflyer:latest
