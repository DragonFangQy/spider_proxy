#!/usr/bin/env bash
tag_suffix=$1
sh util_function.sh
cd ..
tag=${tag_suffix}
#tag="release_20220311"
image="spider_proxy":${tag}

docker build -t ${image} docker/Dockerfile .
# push_image ${image}
