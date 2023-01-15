# coding=utf-8
"""
@FileName：views
@ProjectName：
@CreateTime：2021/12/7 下午4:57
@Author：yangxiaobo
@Email：yangxiaobo@datagrand.com

"""
import os

from flask import send_from_directory
from flask_restful import Resource

from configs.sse_info3_conf import file_base_path


class DownloadFile(Resource):
    def get(self, filename):
        download_file_path = os.path.join(file_base_path, filename)
        return send_from_directory(file_base_path, filename)
