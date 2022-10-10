import traceback
import telnetlib

from itemadapter import ItemAdapter

from spider_proxy.spider_model.spider_proxy_model import SpiderProxyModel
from spider_proxy.spider_pipelines.base_pipeline import BasePipeline


class CN66IPPipeline(BasePipeline):

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        item_dict = adapter.asdict()
        spider_proxy_model = SpiderProxyModel(**item_dict)

        try:
            telnetlib.Telnet(host=spider_proxy_model.ip, port=spider_proxy_model.port, timeout=10)
            self._session_add_model_auto_commit(spider_proxy_model)

        except Exception as e:
            traceback.print_exc()

        return item
