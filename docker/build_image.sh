#!/usr/bin/env bash
tag_suffix=$1
source util_function.sh
cd ..
tag="output_"${tag_suffix}
#tag="release_20220311"
image="dockerhub.datagrand.com/idps/sseinfo3_middle_service":${tag}

build_image ${image} docker/Dockerfile .
push_image ${image}
