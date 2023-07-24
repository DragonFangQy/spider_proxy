

from abc import ABCMeta, abstractmethod
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

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.url_format = self.get_url_format()
        self.re_compile = self.get_re_compile()
        self.my_logger = my_logger
        self.my_logger._Logger__logger.name = self.__class__.__name__
        
    @abstractmethod
    def get_url_format(self):
        pass

    @abstractmethod
    def get_re_compile(self):
        pass

    # @property
    # def empty_page_threshold(self):
    #     return self.empty_page_threshold
    
    # @property.setter
    # def empty_page_threshold(self, value):
    #     self.empty_page_threshold = value

    @abstractmethod
    def parse_data(self,*args, **kwargs):
        pass
    
    def _get_page_num(self, select_obj):
        pass

    def _set_page_total(self, page_num):
        for page in range(self.start_page_num, page_num + 1):
            if page not in self.page_total:
                self.page_total.append(page)
