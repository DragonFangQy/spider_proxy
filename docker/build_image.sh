#!/usr/bin/env bash
tag_suffix=$1
source util_function.sh
cd ..
tag=${tag_suffix}
#tag="release_20220311"
image="spider_proxy":${tag}

build_image ${image} docker/Dockerfile .
# push_image ${image}
