import time
from typing import List

from celery.utils.log import worker_logger

from services.ideas_services import IdeasService
from task import celery_app


@celery_app.task(queue="main_queue")
def send_overtimed_message_tasks():
    """获取超时备忘录并且发送信息"""
    ideas = IdeasService.get_overtimed_ideas(60)
    worker_logger.info("获取到%s个超时任务", len(ideas))
    send_message.delay([{"title": i.title} for i in ideas])


@celery_app.task
def send_message(tasks_list: List[dict]):
    """发送信息，假如这里是发送邮件则是一个典型的异步任务"""
    for task in tasks_list:
        worker_logger.warning("你有一个超时任务%s，请赶快查看。", task['title'])
        time.sleep(10)
