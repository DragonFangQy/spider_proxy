# coding=utf-8
"""
@FileName：data_input
@ProjectName：
@CreateTime：2021/12/7 上午10:07
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
from datetime import datetime
from sqlalchemy import Column, NVARCHAR, INT, DATETIME
from .base_entity import BaseEntity


class DownFilesEntity(BaseEntity):
    __tablename__ = "di_down_file"
    __table_args__ = {"comment": "数据输入接口，文件下载表"}

    #         fild id  文件id
    #         audit item id 审核记录id
    #         source
    #         com_name
    #         anmt_date
    #         rep_type_code
    #         rep_type
    #         src_url
    #         json_data
    file_id = Column(NVARCHAR(100), comment="文件id", default="")
    audit_item_id = Column(NVARCHAR(100), comment="审核记录id", default="")
    company_full_name = Column(NVARCHAR(100), comment="发行人公司全称", default="")
    publish_date = Column(NVARCHAR(20), comment="披露日期", default="")
    file_version_code = Column(NVARCHAR(20), comment="报告类型编码", default="")  # FileVersionEnum
    file_version = Column(NVARCHAR(20), comment="报告类型", default="")  # FileVersionEnum
    file_path = Column(NVARCHAR(200), comment="网站端文件落地路径", default="")
    file_name = Column(NVARCHAR(100), comment="文件唯一名称", default="")
    file_title = Column(NVARCHAR(100), comment="披露文件的标题", default="")
    source = Column(NVARCHAR(100), comment="数据来源", default="DG")
    json_data = Column(NVARCHAR(2000), comment="json object data", default="")
    file_update_time = Column(NVARCHAR(20), comment="文件更新时间", default="")

    extract_id = Column(INT, comment="抽取id", default=0)
    extract_last_update_time = Column(DATETIME, default=datetime.now, comment="抽取更新时间", index=True)

    bulletin_type_code = Column(INT, comment="临时公告类别编码", default=0)
    bulletin_type_desc = Column(NVARCHAR(64), comment="临时公告类别描述", default="")
    security_code = Column(NVARCHAR(16), comment="上市公司代码", default="")
    bulletin_type = Column(NVARCHAR(200), comment="公告类别名称", default="")

    feature_type_id = Column(INT, comment="功能类型 ID", default=0)
    doc_type_id = Column(INT, comment="文档类型 ID", default=0)