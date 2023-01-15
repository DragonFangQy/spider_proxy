from typing import Dict, Iterable, List, Optional
from weakref import WeakValueDictionary

from sqlalchemy import and_, or_

from configs.sysconf import MAX_PAGE_SIZE
from entities.base_entity import BaseEntity, BaseEntityDeleted
from initialization.logger_process import logger
from . import session

_entities_models = WeakValueDictionary()


class ModelMetaClass(type):

    def __new__(mcs, name, bases, attrs):
        if '_entity' not in attrs:
            raise AttributeError("class {} should set these class attributes: _entity".format(name))

        filters = attrs.get("_filter_keys") or []
        ranges = attrs.get("_range_filter_keys") or []
        likes = attrs.get("_like_filter_keys") or []

        children = attrs.get("_children")
        if children:
            _children = list()
            for child in children:
                if len(child.split(".")) != 2:
                    raise AttributeError("child should be set like ChildrenEntiy.parent_id")
                _children.append(child.split("."))
            attrs['_children'] = _children

        cls = type.__new__(mcs, name, bases, attrs)
        cls._entities_models = _entities_models

        if attrs.get("_entity"):
            entity = attrs.get("_entity")
            does_not_exists = (set(filters) | set(ranges) | set(likes)) - set(entity.__table__.columns.keys())
            if does_not_exists:
                raise AttributeError(f"class {entity.__name__} does not have attrs {does_not_exists}")

            cls._entities_models[entity.__name__] = cls

        return cls


class BaseModel(metaclass=ModelMetaClass):
    _entity: BaseEntity.__class__ = None

    # filters
    _filter_keys: List = None
    _range_filter_keys: List = None
    _like_filter_keys: List = None

    # children
    _children: List[str] = None

    @classmethod
    def get_all(cls, active_only: bool = True) -> List["BaseModel._entity"]:
        """
        根据id获取entity对象，该方法设置了默认最大分页，
        请修改配置中的MAX_PAGE_SIZE来修改默认最大分页

        :param active_only: 是否包含软删除的记录, defaults to False
        :type active_only: bool, optional
        :return: 查询的entity对象列表
        """
        _, entity_list = cls.get_by_filter(limit=MAX_PAGE_SIZE, active_only=active_only)
        return entity_list

    @classmethod
    def get_by_id(cls, _id: int, active_only: bool = True) -> Optional["BaseModel._entity"]:
        """根据id获取entity对象

        :param _id: 主键值
        :type _id: int
        :param active_only: 是否包含软删除的记录, defaults to False
        :type active_only: bool, optional
        """
        q = cls._entity.active_query if active_only else cls._entity.query
        q = q.filter(cls._entity.id == _id)
        return q.first()

    @classmethod
    def get_by_id_list(cls, id_list: Iterable, active_only: bool = True) -> List["BaseModel._entity"]:
        """根据主键列表获取entity列表

        :param id_list: id的列表或者集合
        :type id_list: List
        :param active_only: 是否包含软删除的记录, defaults to False
        :type active_only: bool, optional
        """
        q = cls._entity.active_query if active_only else cls._entity.query
        q = q.filter(cls._entity.id.in_(id_list))
        return q.all()

    @classmethod
    def get_all_by_filter(cls,
                          order_by: str = "create_time",
                          order_by_desc: bool = True,
                          active_only: bool = True,
                          **kwargs) -> List["BaseModel._entity"]:
        """
        根据过滤条件获取所有的entity，去除了LIMIT的限制，
        因此可能是一个危险操作
        """
        query = cls._get_full_query(order_by, order_by_desc, active_only, **kwargs)
        return query.all()

    @classmethod
    def get_by_filter(cls,
                      order_by: str = "create_time",
                      order_by_desc: bool = True,
                      offset: int = 0,
                      limit: int = 10,
                      require_count: bool = True,
                      active_only: bool = True,
                      **kwargs) -> tuple:
        """根据条件过滤entity列表，该方法返回一个两个元素的元组
            第一个值为count，代表经过过滤之后总共获取的entity个数
            第二个值为list，为经过排序和切片取值过后的entity列表

        :param order_by: 排序字段, defaults to "create_time"
        :type order_by: str, optional
        :param order_by_desc: 是否倒序, defaults to True
        :type order_by_desc: bool, optional
        :param offset: offset, defaults to 0
        :type offset: int, optional
        :param limit: limit, defaults to 10
        :type limit: int, optional
        :param require_count: 是否返回经过条件过滤之后的合计值，
                              这个方法将单独进行一次sql中的select
                              操作，会影响效率。默认进行查询。
        :type require_count: bool, optional
        :param active_only: 是否包含软删除的记录, defaults to True
        :type active_only: bool, optional
        :param **kwargs:
            过滤条件以关键字的形式传入，关键字过滤的方式在以下几个类属性中设置。
                _filter_keys: List：            使用 == 过滤,   and 相连；
                _range_filter_keys: List        使用<= >= 过滤，and 相连，要求参数一定是一个包含两个要素（start,end)的序列；
                _like_filter_keys: List         使用like过滤，  or相连，实参会自动被加上左右模糊；

        :return: count, entity_list
        """

        query = cls._get_full_query(
            order_by,
            order_by_desc,
            active_only,
            **kwargs,
        )
        count = query.count() if require_count else 0
        q = query.limit(limit).offset(offset)
        return count, q.all()

    @classmethod
    def create(cls, **entity) -> "BaseModel._entity":
        """创建一个Entity
            这个方法应该在不同的Model中被重写，应该有更加详细的函数参数。

        :param **entity 需要传入的字段
        """
        entity = cls._entity(**entity)
        session.add(entity)
        session.flush()
        return entity

    @classmethod
    def bulk_create(cls, entity_list: List[Dict]) -> List:
        """批量创建Entity

        :param entity_list 需要创建的entity信息列表
        """
        entity_list = [cls._entity(**entity) for entity in entity_list]
        session.bulk_save_objects(entity_list, return_defaults=True)
        session.flush()
        return entity_list

    @classmethod
    def delete(cls, _id: int, force_delete=False):
        """删除entity

        :param _id: entity的主键
        :type _id: int
        :param force_delete: 是否硬删除, defaults to False
        :type force_delete: bool, optional
        """

        cls._delete_children([_id], force_delete)
        q = session.query(cls._entity).filter(cls._entity.id == _id)

        if force_delete:
            q.delete(synchronize_session=False)
        else:
            delete_dict = {"active": False}
            q.update(delete_dict, synchronize_session=False)
        session.flush()

    @classmethod
    def bulk_delete_by_filter(cls, force_delete=False, **kwargs):
        """根据条件进行删除，这个一般来说会在级联删除中比较有用"""

        query = cls._get_filtered_query(active_only=True, **kwargs)
        parent_ids = [res.id for res in session.query(cls._entity.id).filter(cls._get_filter(**kwargs)).all()]

        cls._delete_children(parent_ids, force_delete)

        session.query(cls._entity.id).filter(query)
        if force_delete:
            query.delete(synchronize_session=False)
        else:
            delete_dict = {"active": False}
            query.update(delete_dict, synchronize_session=False)
        session.flush()

    @classmethod
    def bulk_delete(cls, id_list: List[int], force_delete=False):
        """根据id批量删除entity

        :param id_list: entity主键列表
        :type id_list: list
        :param force_delete: 是否硬删除, defaults to False
        :type force_delete: bool, optional
        """
        cls._delete_children(id_list, force_delete)

        q = session.query(cls._entity).filter(cls._entity.id.in_(id_list))
        if force_delete:
            q.delete(synchronize_session=False)
        else:
            delete_dict = {"active": False}
            q.update(delete_dict, synchronize_session=False)
        session.flush()

    @classmethod
    def update(cls, _id: int, **kwargs) -> Optional["BaseModel._entity"]:
        """更新entity, 需要更新的key-value通过不定关键字参数传入

        :param _id: entity主键
        :type _id: int
        """
        entity = cls._entity.query.get(_id)
        if not entity:
            return

        entity.auto_set_attr(**kwargs)

        session.flush()
        session.refresh(entity)
        return entity

    @classmethod
    def bulk_update(cls, entity_list: List[Dict]):
        """批量更新entity。
        entity_list中必须包含entity的主键键值对，一般是id，即[dict(id=1, foo="foo", bar="bar")]

        :param entity_list: 需要更新的entity字典列表，必须包含entity的主键键值对
        :type entity_list: List[Dict]
        """
        session.bulk_update_mappings(cls._entity, entity_list)
        session.flush()

    @classmethod
    def _get_filtered_query(cls, active_only, **kwargs):
        """获取经过过滤的BaseQuery对象"""
        q = cls._entity.active_query if active_only else cls._entity.query
        # handle filter_keys
        f = cls._get_filter(**kwargs)
        return q.filter(f)

    @classmethod
    def _get_filter(cls, **kwargs):
        """根据Model允许的过滤条件获取filter对象"""
        and_list = list()
        for key in cls._filter_keys or []:
            if key in kwargs and kwargs[key] is not None:  # FIXME: 这个可能不能过滤None的查询
                value = kwargs[key]
                if isinstance(value, (list, tuple, set)) and not isinstance(value, (str, bytes)):
                    and_list.append(getattr(cls._entity, key).in_(value))
                else:
                    and_list.append(getattr(cls._entity, key) == value)

        # handle range_filter_keys
        for key in cls._range_filter_keys or []:
            start, end = kwargs.get(key) or (None, None)
            if start:
                and_list.append(getattr(cls._entity, key) >= start)
            if end:
                and_list.append(getattr(cls._entity, key) <= end)

        # handle like_filter_keys
        like_filters = [
            getattr(cls._entity, key).like(f"%{kwargs[key]}%") for key in cls._like_filter_keys or []
            if kwargs.get(key) is not None
        ]  # FIXME: 这个可能不能过滤None的查询
        return and_(*and_list, or_(*like_filters))

    @classmethod
    def _get_full_query(cls,
                        order_by: str = "create_time",
                        order_by_desc: bool = True,
                        active_only: bool = True,
                        **kwargs):
        """获取完整的query，1. 获取 filter 2. 获取 filtered_query 3. 添加order_by """
        query = cls._get_filtered_query(active_only, **kwargs)
        if order_by:
            order_column = getattr(cls._entity, order_by)
            order_stmt = order_column.desc() if order_by_desc else order_column.asc()
            query = query.order_by(order_stmt)
        return query

    @classmethod
    def _delete_children(cls, parent_ids, force_delete=False, **kwargs):
        """
        支持级联软删除子表中的数据
        需要在父表的Model中设置子表的 classname 和 外键名称如
        class ParentModel(BaseModel):
            _children = ["ChildrenEntity.parent_id"]
        """
        if cls._children:
            for child, fk in cls._children:
                child_model = cls._entities_models.get(child)
                if not child_model:
                    raise RuntimeError(f"ChildEntiy {child} is not found!")

                if fk not in child_model._filter_keys:
                    logger.warning(f"Child Model {child_model.__name__}'s filters doesn't contain foreign key {fk}")
                child_model.bulk_delete_by_filter(force_delete, **{fk: parent_ids})

class BaseDeletedModel(BaseModel):
    _entity: BaseEntityDeleted.__class__ = None
