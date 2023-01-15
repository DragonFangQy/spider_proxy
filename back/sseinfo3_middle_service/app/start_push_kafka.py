# coding=utf-8
"""
@FileName：test_demo
@ProjectName：
@CreateTime：2022/4/27 上午11:45
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
import time

from kafka import KafkaProducer
from krbcontext import krbContext

from app import app
from flask import g

from configs.push_kafka_conf import kafka_context, kafka_producer
from configs.sse_info3_conf import time_interval, time_unit
from initialization.logger_process import logger, logger_exception


def run():
    conf_interval = get_interval_s()
    diff_interval = 0

    with krbContext(**kafka_context):
        producer = KafkaProducer(
            **kafka_producer
            , value_serializer=lambda v: v.encode('utf-8')
        )

        while True:
            logger.info("push_kafka start")
            try:
                start = time.time()

                with app.app_context():
                    with app.test_client() as c:
                        g.time_interval = conf_interval \
                                            if diff_interval < conf_interval \
                                            else diff_interval

                        g.producer = producer

                        try:
                            result = c.post('/api/v2/push_kafka')
                            logger.info(result.get_json())
                        except Exception as e:
                            print(e)

                diff_interval = int(time.time() - start)

                if diff_interval < conf_interval:
                    time.sleep(conf_interval - diff_interval)

            except Exception as e:
                logger_exception()


def get_interval_s():
    """
    获取时间间隔的秒数

    """
    H_ = 60 * 60
    d_ = H_ * 24

    time_unit_dict = {
        "Y": d_ * 365
        , "m": d_ * 30
        , "d": H_ * 24
        , "H": H_
        , "M": 60
        , "S": 1
    }

    interval = time_interval * time_unit_dict[time_unit]
    return interval


def isValid( s):
    """
    :type s: str
    :rtype: bool
    """
    temp_dict = {
        ")": "(",
        "}": "{",
        "]": "[",
    }

    valid_list = ["(",
                  "{",
                  "["]

    left_list = []
    for item in s:
        if item in valid_list:
            left_list.append(item)
        else:
            left_pop = left_list[-1]
            if left_pop == temp_dict[item]:
                left_list.pop()
                continue
    if len(left_list) == 0:
        return "true"

    return "false"
if __name__ == '__main__':
    isValid("()")
