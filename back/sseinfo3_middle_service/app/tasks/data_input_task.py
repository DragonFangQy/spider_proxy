# coding=utf-8
"""
@FileName：data_input_task
@ProjectName：
@CreateTime：2021/12/8 下午2:55
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""

from celery.utils.log import worker_logger

from configs.sse_info3_conf import input_file_by_api
from services.data_input_services import DataInputService
from task import celery_app

@celery_app.task()
def data_input():

    if input_file_by_api.lower() == "true":
        DataInputService().down_files()
    else:
        DataInputService().down_files_kafka()
