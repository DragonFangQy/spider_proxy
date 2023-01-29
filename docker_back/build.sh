#!/bin/bash


PROJECT_NAME=$(pwd | rev | awk '{split($0, a, "\/"); print tolower(a[2])}' | rev)
echo '5'
echo 'PROJECT_NAME=' ${PROJECT_NAME}
cd $(dirname $0)/../
DOCKERVERSION=`date +%Y%m%d%H%M`"_"`git log | head -1 | awk '{print $2}' | cut -c 1-10`

# build..
docker build --build-arg PROJECT_DIRNAME=${PROJECT_NAME} \
              -t ${PROJECT_NAME}:${DOCKERVERSION} \
              -f docker/Dockerfile .



