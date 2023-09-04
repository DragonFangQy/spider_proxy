#!/bin/bash

tag_suffix=$1
# sh util_function.sh
source ./util_function.sh
cd ..
tag=${tag_suffix}
#tag="release_20220311"
image=${tag}


# 通过 tr 切分 并获取列表最后一个元素
array=(`echo $image | tr '_' ' '` ) 
last_element_index=$((${#array[*]}-1))
last_element=(${array[$last_element_index]})
echo 'last_element:' $last_element

# 最后是 debug, 则build debug 镜像
if [ $last_element == 'debug' ]
then
    # build 镜像
    echo "docker build debug"
    build_image ${image} docker/Dockerfile_debug .
else
    # gitlab test
    echo "gitlab test"
    ls -al /usr/bin/ | grep docker
    ls -al /var/run/ | grep docker.sock

    # build 镜像
    echo "docker build"
    build_image ${image} docker/Dockerfile .
fi


docker login

docker push ${image} 
echo ${image}
