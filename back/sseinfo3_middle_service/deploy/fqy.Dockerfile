FROM harbor.datagrand.com/base/python-3.7.0@sha256:19bbe379fdc7362c937041e35fa6cc4317a1d8862c08abfc76597ea6d7b5db8b

LABEL MAINTAINER="smile_joker1514@163.com"

ARG app_dir=/app

COPY entrypoint.sh /


RUN sudo chmod 755 /entrypoint.sh && \
 	sudo mkdir -p ${app_dir}

ENV FLASK_APP=${app_dir}/app/app.py

COPY app ${app_dir}/app
COPY data ${app_dir}/data
COPY logs ${app_dir}/logs

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
