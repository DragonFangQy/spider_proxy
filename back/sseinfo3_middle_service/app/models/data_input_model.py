# coding=utf-8
"""
@FileName：data_input
@ProjectName：
@CreateTime：2021/12/7 下午3:29
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""

from sqlalchemy import or_, and_, func
from entities.data_input_entity import DownFilesEntity
from initialization.logger_process import logger
from . import commit
from .base_model import BaseModel
from .extract import ExtractModel


class DownFileModel(BaseModel):
    _entity = DownFilesEntity
    # _like_filter_keys = ["title"]
    _filter_keys = ["file_id", "file_name", "extract_id"]
    _range_filter_keys = ["create_time", "last_update_time"]

    @classmethod
    def get_by_file_id(cls, file_id: int, active_only: bool = True):
        """
        根据file_id 获取entity对象

        :param _id: 主键值
        :type _id: int
        :param active_only: 是否包含软删除的记录, defaults to False
        :type active_only: bool, optional
        """
        q = cls._entity.active_query if active_only else cls._entity.query
        q = q.filter(cls._entity.file_id == file_id)
        return q.first()

    @classmethod
    def get_by_extract_id(cls, extract_id: int, active_only: bool = True):
        """
        根据file_id 获取entity对象

        :param _id: 主键值
        :type _id: int
        :param active_only: 是否包含软删除的记录, defaults to False
        :type active_only: bool, optional
        """
        q = cls._entity.active_query if active_only else cls._entity.query
        q = q.filter(cls._entity.extract_id == extract_id)
        return q.first()

    @classmethod
    def get_data_by_extract_list(cls, extract_list, active_only: bool = True):
        """
        根据抽取结果列表，过滤并获取数据

        :param _id: 主键值
        :type _id: int
        :param active_only: 是否包含软删除的记录, defaults to False
        :type active_only: bool, optional
        """

        filter_list = []
        for extract_obj in extract_list:

            filter_list.append(and_(cls._entity.extract_id == extract_obj.id,
                                    func.ifnull(cls._entity.extract_last_update_time, cls._entity.last_update_time)
                                     != extract_obj.last_update_time))

        q = cls._entity.active_query if active_only else cls._entity.query
        q = q.filter(and_(or_(*filter_list)))

        count = q.count()

        if count == 0:
            logger.info("PushKafkaService get_data_by_extract_list 无下载数据")
            raise ValueError("PushKafkaService get_data_by_extract_list 无下载数据")

        return q.all()

    @classmethod
    @commit
    def update_extract_last_update_time(cls, extract_id):
        """
        更新extract_last_update_time

        """
        down_file_obj = cls.get_by_extract_id(extract_id)

        extract_model = ExtractModel.get_by_id(extract_id)

        DownFileModel.update(down_file_obj.id, extract_last_update_time=extract_model.last_update_time)