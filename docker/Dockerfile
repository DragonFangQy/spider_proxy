FROM workdragonfang/docker_build_python:3_10_9_v_103

ENV PROJECT_DIRNAME="spider_proxy"

# prepare install
RUN mkdir /${PROJECT_DIRNAME}&&\
        apt-get update --allow-releaseinfo-change && apt-get -y install gcc libkrb5-dev python3-dev

WORKDIR /${PROJECT_DIRNAME}
COPY requirements/requirements.txt /${PROJECT_DIRNAME}/requirements.txt
COPY docker/ /${PROJECT_DIRNAME}/docker/
COPY db_repo/ /${PROJECT_DIRNAME}/db_repo/
COPY alembic_repos/ /${PROJECT_DIRNAME}/alembic_repos/

# install python packages.
RUN chmod -R 777 docker/ db_repo/ alembic_repos/ &&\
    pip3 config --global set global.index-url https://mirrors.aliyun.com/pypi/simple/ &&\
    pip3 config --global set install.trusted-host mirrors.aliyun.com &&\
    pip3 install --quiet --upgrade pip &&\
    pip3 install --quiet -r requirements.txt
# RUN pip3 uninstall pyOpenSSL &&\
#     pip3 install pyOpenSSL==22.0.0

# add code.
COPY spider_proxy /${PROJECT_DIRNAME}/spider_proxy
COPY scrapy.cfg /${PROJECT_DIRNAME}/scrapy.cfg
COPY entrance.py /${PROJECT_DIRNAME}/entrance.py
COPY entrance.py /${PROJECT_DIRNAME}/alembic.ini


CMD ./docker/run_app.sh
