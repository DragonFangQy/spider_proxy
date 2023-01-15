# coding=utf-8
"""
@FileName：push_kafka_conf
@ProjectName：
@CreateTime：2022/5/19 下午6:25
@Author：fangqingyou
@Email：fangqingyou@datagrand.com

"""
from utils.sse_info3_util import FileCategoryEnum

topic_dict = {
    FileCategoryEnum.common_prospectus.value: "ANNOUNCEMENT.STRUCT_STAR",    # 招股书
    FileCategoryEnum.common_temporary_announcement.value: "ANNOUNCEMENT.STRUCT_TEMPORARY",      # 临时公共
    FileCategoryEnum.common_temporary_1001.value: "ANNOUNCEMENT.STRUCT_TEMPORARY",      # 临时公共
}

# kafka KafkaProducer
kafka_context = {
    "using_keytab": True

    # 用户
    , "principal": "announcedg@SSE.COM.CN"

    # 认证文件路径
    , "keytab_file": "/sseinfo3_middle_service/app/configs/announcedg.keytab"

    # , "ccache_file": "/sseinfo3_middle_service/data/cache_file"
}

kafka_producer = {
    # test
    "bootstrap_servers": ['ssebigdata-dn01.devel:9092', 'ssebigdata-dn02.devel:9092',
              'ssebigdata-dn03.devel:9092', 'ssebigdata-dn04.devel:9092']

    # # product
    # "bootstrap_servers": ["ssebigdata-dn01.prod:9092","ssebigdata-dn02.prod:9092"
    #                 ,"ssebigdata-dn03.prod:9092","ssebigdata-dn04.prod:9092"
    #                 ,"ssebigdata-dn05.prod:9092"]

    , "security_protocol": "SASL_PLAINTEXT"
    , "sasl_mechanism": "GSSAPI"
    , "api_version": (3, 0, 0)
    , "request_timeout_ms": 1000 * 60 * 5  # 毫秒为单位
    , "retries": 3
    , "max_block_ms": 1000 * 60 * 5   # 毫秒为单位
    , "acks": "all"
}
