# coding=utf-8
"""
@FileName：tags_model
@ProjectName：
@CreateTime：2022/5/18 下午6:41
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
from entities.tags_entity import TagsEntity
from models.base_model import BaseModel


class TagsModel(BaseModel):
    _entity = TagsEntity
    _filter_keys = ["tag_type_id"]
    # _range_filter_keys = ["last_update_time"]