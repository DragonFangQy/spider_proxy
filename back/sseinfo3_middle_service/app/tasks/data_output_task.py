# coding=utf-8
"""
@FileName：data_output_task
@ProjectName：
@CreateTime：2022/2/18 下午4:01
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
from services.push_kafka import PushKafkaService
from task import celery_app

@celery_app.task()
def push_kafka():
    PushKafkaService().logic()