# coding=utf-8
"""
@FileName：views
@ProjectName：
@CreateTime：2021/12/9 上午9:40
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
from flask_restful import Resource

from initialization.logger_process import logger_exception, logger
from services.push_kafka import PushKafkaService

class PushKafka(Resource):

    def post(self):

        logger.info("PushKafka start")

        try:
            result = PushKafkaService().logic()
        except Exception as e:
            logger_exception()
            return {"status": "failed", "message": "数据输出失败", "data": {}}, 500

        logger.info("PushKafka end")
        return {"status": "success", "message": "数据输出成功", "data": result}, 200