#!/bin/bash
source /Users/dragonfang/Documents/workspace/P_001_Python/spider_proxy/venv_spider_proxy/bin/activate
cd /Users/dragonfang/Documents/workspace/P_001_Python/spider_proxy/db_repo/

python manage.py version_control   
python manage.py upgrade