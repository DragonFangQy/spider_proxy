import re
import time
import scrapy
from scrapy import Request, Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from spider_proxy.spider_items.cn_66ip_item import Cn66IPItem, Cn66IPItemEnum
from spider_proxy.spiders.base_spider import BaseSpider
from spider_proxy.utils.utils_proxy import get_proxy_url


class ComSeofangfaipSpider(BaseSpider):
    name = 'com_seofangfa'
    allowed_domains = ['seofangfa.com']
    custom_settings={
        "DOWNLOAD_DELAY": 300, 
        "AUTOTHROTTLE_START_DELAY":300, 
        "AUTOTHROTTLE_MAX_DELAY": 300
        }
    
    # test
    # page_total = [50,51]
    # start_page_num = 50

    def get_url_format(self):
        return "https://proxy.seofangfa.com/?{count_num}"

    def get_re_compile(self):
        return re.compile(".*?www.89ip.cn/index_(?P<page>\d+).html")
    
    def start_requests(self):
        for page in self.page_total:
            
            url=self.url_format.format(count_num=page)
            proxy_url = get_proxy_url()

            self.my_logger.info(f"page_total：{len(self.page_total)},当前 page：{page}\n url: {url}\n proxy_url: {proxy_url}\n")

            yield Request(url=url, meta={"proxy": proxy_url,}, dont_filter=True)
            yield Request(url=url, dont_filter=True)

            self._set_page_total(len(self.page_total))

    def parse(self, response):

        select_obj = Selector(response, type="html")

        # 找到页面中的表格，从表格中获取数据
        tr_so_list = select_obj.xpath("""//table[@class="table"]/tbody/tr""")

        for tr_so in tr_so_list:

            "IP	端口	响应时间	位置	最后验证时间"
            item = Cn66IPItem()
            item_loader = ItemLoader(item=item, selector=tr_so)
            item_loader.default_output_processor = TakeFirst()
            item_loader.add_xpath(Cn66IPItemEnum.ip.value, "./td[position()=1]/text()")
            item_loader.add_xpath(Cn66IPItemEnum.port.value, "./td[position()=2]/text()")
            item_loader.add_xpath(Cn66IPItemEnum.location.value, "./td[position()=4]/text()")
            yield item_loader.load_item()
        
        # yield from self.parse_data(response=response)
    
    def parse_data(self,*args, **kwargs):
        pass