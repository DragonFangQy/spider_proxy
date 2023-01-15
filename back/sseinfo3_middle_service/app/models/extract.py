# coding=utf-8
"""
@FileName：extract
@ProjectName：
@CreateTime：2022/2/17 下午3:51
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
from entities.extract import ExtractEntity
from initialization.logger_process import logger
from models.base_model import BaseDeletedModel

class ExtractModel(BaseDeletedModel):
    _entity = ExtractEntity
    # _filter_keys = ["file_id", "file_name", "extract_id"]
    _range_filter_keys = ["last_update_time"]

    @classmethod
    def get_data_by_time_status(cls, last_update_time, active_only: bool = True):
        """
        根据 last_update_time 和 status 过滤抽取数据

        # 抽取成功 5；  已审核 8
        status in (5,8)

        :param _id: 主键值
        :type _id: int
        :param active_only: 是否包含软删除的记录, defaults to False
        :type active_only: bool, optional
        """

        q = cls._entity.active_query if active_only else cls._entity.query
        q = q.filter(cls._entity.last_update_time >= last_update_time,
                     cls._entity.status.in_([5, 8]))

        count = q.count()

        if count == 0:
            logger.info("PushKafkaService get_data_by_time_status 无抽取数据")
            raise ValueError("PushKafkaService get_data_by_time_status 无抽取数据")

        return q.all()

