#!/bin/bash

export PKG_DIR="python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.7 \
    pip install -r requirements.txt --no-deps -t ${PKG_DIR}

rm -fr ${PKG_DIR}/*.dist-info
rm -fr ${PKG_DIR}/__pycache__
