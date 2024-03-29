

from abc import ABCMeta, abstractmethod
import scrapy


class BaseSpider(scrapy.Spider, metaclass=ABCMeta):
    # name = 'cn_66ip'
    # allowed_domains = ['66ip.cn']

    page_total = [1, 2]

    url_format = None
    re_compile = None

    empty_page_list = []
    empty_page_threshold = 5

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.url_format = self.get_url_format()
        self.re_compile = self.get_re_compile()
        
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
    
    @abstractmethod
    def _get_page_num(select_obj):
        pass

    def _set_page_total(self, page_num):
        for page in range(1, page_num + 1):
            if page not in self.page_total:
                self.page_total.append(page)
