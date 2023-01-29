FROM dockerhub.datagrand.com/data-dev/python-3.8.11:base-ssh

COPY docker/conf/krb5.conf /etc
COPY docker/conf/hosts /etc

# prepare install
RUN mkdir /sseinfo3_middle_service&&\
        apt-get update --allow-releaseinfo-change && apt-get -y install gcc libkrb5-dev

WORKDIR /sseinfo3_middle_service
COPY requirements/requirements.txt /sseinfo3_middle_service/requirements.txt

# install python packages.
# RUN mkdir -p /root/.ssh
# ADD docker/id_rsa /root/.ssh/id_rsa
# RUN chmod 600 /root/.ssh/id_rsa
RUN echo StrictHostKeyChecking no > /root/.ssh/config &&\
    pip install --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt -i https://pypi.douban.com/simple/

# add code.
COPY deploy /sseinfo3_middle_service/deploy
COPY app /sseinfo3_middle_service/app
COPY data /sseinfo3_middle_service/data
COPY logs /sseinfo3_middle_service/logs

# RUN rm -rf /root/.ssh

RUN cd / \
    && useradd datagrand -u 2329 -m \
    && chmod -R 777 /root \
    && chmod -R 777 /sseinfo3_middle_service \
    && ls / | grep -v bin | grep -v boot | grep -v etc | grep -v lib | grep -v media | grep -v mnt | grep -v opt | grep -v proc | grep -v srv | grep -v sys | grep -v usr  | xargs -i chown -R datagrand:datagrand {}
USER datagrand
#start
CMD cd deploy && sh start.sh


#FROM harbor.datagrand.com/base/python-3.7.0@sha256:19bbe379fdc7362c937041e35fa6cc4317a1d8862c08abfc76597ea6d7b5db8b
#
#LABEL MAINTAINER="smile_joker1514@163.com"
#
#ARG PROJECT_DIRNAME
#
#RUN sudo mkdir -p sseinfo3_middle_service
#
#ENV FLASK_APP=/sseinfo3_middle_service/app/app.py
#
#COPY deploy sseinfo3_middle_service/deploy
#COPY app sseinfo3_middle_service/app
#COPY data sseinfo3_middle_service/data
#COPY logs sseinfo3_middle_service/logs
#
#ENTRYPOINT ["/usr/bin/tini", "--", "/sseinfo3_middle_service/deploy/start.sh"]
