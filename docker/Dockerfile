FROM python:3.10.8

ENV PROJECT_DIRNAME="spider_proxy"

# prepare install
RUN mkdir /${PROJECT_DIRNAME}&&\
        apt-get update --allow-releaseinfo-change && apt-get -y install gcc libkrb5-dev  python3-dev

WORKDIR /${PROJECT_DIRNAME}
COPY requirements/requirements.txt /${PROJECT_DIRNAME}/requirements.txt
COPY docker/ /${PROJECT_DIRNAME}/docker/
COPY db_repo/ /${PROJECT_DIRNAME}/db_repo/

# install python packages.
RUN chmod -R 777 docker/ db_repo/ &&\
    pip3 config --global set global.index-url https://mirrors.aliyun.com/pypi/simple/ &&\
    pip3 config --global set install.trusted-host mirrors.aliyun.com &&\
    pip3 install --upgrade pip &&\
    pip3 install -r requirements.txt
    # pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# add code.
COPY spider_proxy /${PROJECT_DIRNAME}/spider_proxy
COPY scrapy.cfg /${PROJECT_DIRNAME}/scrapy.cfg
COPY entrance.py /${PROJECT_DIRNAME}/entrance.py


CMD ./docker/run_app.sh
