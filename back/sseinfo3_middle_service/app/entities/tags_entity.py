# coding=utf-8
"""
@FileName：tags_entity
@ProjectName：
@CreateTime：2022/5/18 下午5:32
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
import enum

from sqlalchemy import Column, String, VARCHAR, TEXT
from sqlalchemy.dialects.mysql import INTEGER, LONGTEXT

from entities.base_entity import BaseEntityStatus


class NodeTypeEnum(enum.Enum):
    tag = 'tag'
    group = 'group'

class TagsEntity(BaseEntityStatus):
    __tablename__ = "tags"
    __bind_key__ = "contract"  # 这里为SQLALCHEMY_BINDS中其他数据库的key

    tag_type_id = Column(INTEGER, nullable=False, index=True, doc='文档类型 ID')
    name = Column(String(256), nullable=False, default="", doc='字段名称')

    desc = Column(String(512), default="", doc='字段描述')
    data_type = Column(String(32), default="", doc='数据类型')
    color = Column(String(32), default="", doc='颜色配置')
    index = Column(LONGTEXT, doc="排序，同tag_type_id支持以index大小进行展示排序", default="[]")
    node_type = Column(VARCHAR(64), nullable=False, doc='节点类型："tag"、"group" 默认 "tag"')
    parent_id = Column(LONGTEXT, doc='父节点 ID', default="[]")
    extended = Column(TEXT, default="")

    def is_parent(self):
        return self.node_type == NodeTypeEnum.group.value
