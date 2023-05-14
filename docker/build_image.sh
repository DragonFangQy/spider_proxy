#!/usr/bin/env bash
tag_suffix=$1
# sh util_function.sh
source util_function.sh
cd ..
tag=${tag_suffix}
#tag="release_20220311"
image="spider_proxy":${tag}

echo "docker build"
# docker build -t ${image} -f docker/Dockerfile .
build_image ${image} docker/Dockerfile .
# push_image ${image}
