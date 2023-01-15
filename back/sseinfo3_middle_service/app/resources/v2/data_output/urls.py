# coding=utf-8
"""
@FileName：urls
@ProjectName：
@CreateTime：2021/12/9 上午9:40
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""

from ... import Api
from .. import v2
from .views import PushKafka

api = Api(app=v2)

api.add_resource(PushKafka, "/push_kafka")