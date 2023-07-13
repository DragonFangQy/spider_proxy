import traceback

from itemadapter import ItemAdapter

from spider_proxy.spider_model.spider_proxy_model import SpiderProxyModel
from spider_proxy.spider_pipelines.base_pipeline import BasePipeline
# from spider_proxy.utils.utils_mq import get_mq_producer
from spider_proxy.utils.utils_kafka import kafka_producer, KafkaProducer

class CN66IPPipeline(BasePipeline):

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        item_dict = adapter.asdict()
        spider_proxy_model = SpiderProxyModel(**item_dict)

        try:
            # telnetlib.Telnet(host=spider_proxy_model.ip, port=spider_proxy_model.port, timeout=10)
            # self._session_add_model_auto_commit(spider_proxy_model)
            # get_mq_producer().send_message(spider_proxy_model.to_string())
            
            # 通过 strip 去除特殊字符
            spider_proxy_model.ip               = spider_proxy_model.ip               .strip()
            spider_proxy_model.port             = spider_proxy_model.port             .strip()
            spider_proxy_model.protocol         = spider_proxy_model.protocol         .strip()
            spider_proxy_model.anonymity_type   = spider_proxy_model.anonymity_type   .strip()
            spider_proxy_model.location         = spider_proxy_model.location         .strip()
            spider_proxy_model.network_operator = spider_proxy_model.network_operator .strip()

            kafka_producer.send_message_single(spider_proxy_model.to_string())

        except Exception as e:
            traceback.print_exc()

        return item
