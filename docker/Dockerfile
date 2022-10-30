FROM python:3.10

ARG PROJECT_DIRNAME

# prepare install
RUN mkdir /${PROJECT_DIRNAME}&&\
        apt-get update --allow-releaseinfo-change && apt-get -y install gcc libkrb5-dev  python3-dev

WORKDIR /${PROJECT_DIRNAME}
COPY requirements/requirements.txt /${PROJECT_DIRNAME}/requirements.txt

# install python packages.
RUN pip install --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# add code.
COPY spider_proxy /${PROJECT_DIRNAME}/spider_proxy
COPY scrapy.cfg /${PROJECT_DIRNAME}/scrapy.cfg
COPY entrance.py /${PROJECT_DIRNAME}/entrance.py

#start
# CMD cd deploy && sh start.sh
CMD python entrance.py
