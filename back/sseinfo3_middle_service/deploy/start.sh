# !/bin/bash
echo "SERVICE RUN STATUS: ONLINE !!!"
python3 /sseinfo3_middle_service/app/start_push_kafka.py

#echo '################################ run migrations ################################'

#echo "----初始化数据库----"
#cd $(dirname $0)/..
#flask db upgrade -d app/migrations

#echo "----启动服务----"
#cd app
#gunicorn app:app -c configs/gunicorn_conf.py

#echo "----初始化数据库----"
#PROJECT_NAME=$( find . -name "sseinfo3_middle_service" | rev | awk '{split($0, a, "\/"); print tolower(a[1])}' | rev)
#flask db upgrade -d ${PROJECT_NAME}/app/migrations
#
#echo "----启动服务----"
#cd ${PROJECT_NAME}/app && gunicorn app:app -c configs/gunicorn_conf.py
