#!/usr/bin/env bash
#***********************************************
#	Author:        Jifa
#	Mail:          smile_joker1514@163.com
#	Version:       1.0
#	Date:          2021-12-20
#	FileName:      entrypoint.sh
#	Description:   The test script
#***********************************************


echo "----初始化数据库----"
cd /app/app && flask db upgrade -d migrations


echo "----启动服务----"
cd /app/app && gunicorn app:app -c configs/gunicorn_conf.py
