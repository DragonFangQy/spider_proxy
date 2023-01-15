# coding=utf-8
"""
@FileName：urls
@ProjectName：
@CreateTime：2021/12/7 下午4:56
@Author：yangxiaobo
@Email：yangxiaobo@datagrand.com

"""
from ... import Api
from .. import v2
from .views import DownloadFile

api = Api(app=v2)

api.add_resource(DownloadFile, "/download/<string:filename>")
