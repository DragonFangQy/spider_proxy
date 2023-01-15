from marshmallow.validate import OneOf
from marshmallow_sqlalchemy import auto_field
from marshmallow import fields

from entities.ideas_entity import IdeaEntity
from utils.constant.idea_enum import StateEnum
from .base_schema import BaseSchema, PageMixin


class IdeaSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = IdeaEntity

    level = auto_field(validates=OneOf(StateEnum.__members__.values()), missing=StateEnum.normal.value)


class CreateIdeaSchema(IdeaSchema):

    class Meta(IdeaSchema.Meta):
        fields = ()

    title = auto_field(required=True)
    is_done = auto_field(dump_only=True)
    done_at = auto_field(dump_only=True)


class IdeaListSchema(PageMixin, IdeaSchema):

    class Meta(IdeaSchema.Meta):
        excludes = ('text', )

    start_time = fields.DateTime()  # start_time 在 IdeaEntity 中不存在，因此添加该值，具体如何使用该值可以在 service 层面定义
    end_time = fields.DateTime()
