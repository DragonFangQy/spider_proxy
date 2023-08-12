

from abc import ABCMeta, abstractmethod
from typing import Dict
import scrapy

from spider_proxy.spider_common import config
from spider_proxy.utils.utils_log import my_logger


class BaseSpider(scrapy.Spider, metaclass=ABCMeta):
    # name = 'cn_66ip'
    # allowed_domains = ['66ip.cn']
    
    start_page_num = 1  # 默认从1 开始
    page_total = [i for i in range(start_page_num, start_page_num + config.INIT_PAGE_SIZE)]

    url_format = None
    re_compile = None

    empty_page_list = []
    empty_page_threshold = 5

    request_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.url_format = self.get_url_format()
        self.re_compile = self.get_re_compile()
        self.my_logger = my_logger
        
    @abstractmethod
    def get_url_format(self):
        pass

    @abstractmethod
    def get_re_compile(self):
        pass

    def get_header(self, header: Dict = None):
        if header is None: 
            return self.request_headers
        
        self.request_headers.update(header)
        return self.request_headers

    @abstractmethod
    def parse_data(self,*args, **kwargs):
        pass
    
    def _get_page_num(self, select_obj):
        pass

    def _set_page_total(self, page_num):
        # 已存在 或者 超过 1000，直接返回
        if page_num in self.page_total or len(self.page_total) >= config.MAX_PAGE_SIZE:
            return

        for page in range(self.start_page_num, page_num + 1):
            if page not in self.page_total:
                self.page_total.append(page)
