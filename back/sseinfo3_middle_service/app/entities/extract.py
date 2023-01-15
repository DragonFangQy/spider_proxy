# coding=utf-8
"""
@FileName：extract
@ProjectName：
@CreateTime：2022/2/17 下午3:50
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
from entities.base_entity import BaseEntityDeleted

from sqlalchemy import Column, NVARCHAR, INT, Integer


class ExtractEntity(BaseEntityDeleted):
    __tablename__ = "extract"
    __bind_key__ = "contract"  # 这里为SQLALCHEMY_BINDS中其他数据库的key

    origin_name = Column(NVARCHAR(256), nullable=False, doc="文件原始名称")
    unique_name = Column(NVARCHAR(256), nullable=False, doc='文件在系统内的唯一名称')

    status = Column(  # 抽取成功 5；  已审核 8
        Integer(),
        nullable=False
    )