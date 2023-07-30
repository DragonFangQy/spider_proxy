import re
import datetime

import scrapy
from scrapy import Request, Selector
from scrapy.http import HtmlResponse

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from spider_proxy.spider_items.cn_66ip_item import Cn66IPItem, Cn66IPItemEnum
from spider_proxy.spiders.base_spider import BaseSpider
from spider_proxy.spider_common import config
from spider_proxy.utils.utils_proxy import get_proxy_url



"""
站大爷代理
"""
class ComZdayeSpider(BaseSpider):
    name = 'com_zdaye'
    allowed_domains = ['zdaye.com']
    """
    parse
        add_detail_url_by_parent
            parse_detail    
                add_detail_url_by_brother
                    parse_detail

    parse 调用 add_detail_url_by_parent 解析并添加 详情页 url
    parse_detail 解析详情页，并调用 add_detail_url_by_brother 添加其他详情页面
            
    """
    diff_month = config.ZDAYE_DIFF_MONTH

    # https://www.zdaye.com/dayProxy/ip/335085/1.html
    re_compile_proxy_detail = re.compile("https://www.zdaye.com/dayProxy/ip/(?P<id>\d+)/(?P<page>\d+).html")
    

    def get_url_format(self):
        return "https://www.zdaye.com/dayProxy/{year}/{month}/{page}.html"


    def get_re_compile(self):
        return re.compile(".*?www.zdaye.com/dayProxy/(?P<year>\d+)/(?P<month>\d+)/(?P<page>\d+).html")


    def start_requests(self):

        # 当前月份
        current_datetime = datetime.datetime.now()

        headers_dict = {
            "Referer": "https://www.zdaye.com/",
            "Origin": "https://www.zdaye.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44",
        }

        for i in range(self.diff_month):

            # 获取年份 和 月份
            year, month = current_datetime.strftime("%Y-%m").split("-")

            for page in self.page_total:
                temp_str = year+"_"+month
                url=self.url_format.format(year=year, month=month, page=page)
                proxy_url = get_proxy_url()

                self.my_logger.info(f"page_total：{len(self.page_total)},月份: {temp_str},当前 page：{page}\n url: {url}\n proxy_url: {proxy_url}\n")

                yield Request(url=url, headers=headers_dict, meta={"proxy": proxy_url,})
                yield Request(url=url, headers=headers_dict)

            # 设置时间为本月的第一天
            # 通过timedelta 获取上个月的 年份&月份
            # 并赋值给 current_datetime
            # 通过 for 的方式一直获取 上个月的 年份&月份
            pre_month_datetime = datetime.date(current_datetime.year, current_datetime.month, 1) + datetime.timedelta(days=-1)
            current_datetime = datetime.date(pre_month_datetime.year, pre_month_datetime.month, 1)


    def parse(self, response: HtmlResponse, **kwargs):
        # 解析列表页，添加详情页
        select_obj = Selector(response)
        
        # 调整 self.page_total
        page_num = self._get_page_num(select_obj)
        self._set_page_total(page_num)
        
        yield from self.add_detail_url_by_parent(select_obj, response)
        

    def parse_detail(self, response: HtmlResponse, **kwargs):        
        # 处理详情页的分页器，添加详情页
        select_obj = Selector(response)
        
        yield from self.parse_data(select_obj, response)

        yield from self.add_detail_url_by_brother(response, select_obj)


    def add_detail_url_by_brother(self, response, select_obj):
        """
        添加明细url，通过同胞页面（通过本页的页面选择器添加）
        处理详情页的分页器，添加详情页

        :param response:
        :param select_obj:
        :return:
        """

        source_url = response.request.url
        page_num = self._get_page_num(select_obj)

        # 通过详情页的 页码选择器，将所有页面url 添加到爬取队列
        for page_num in range(1, page_num + 1):

            # 处理来源url , 替换来源页面的页码
            # http://xxxxxx/1.html  ==> http://xxxxxx/1.html
            source_url_list = source_url.split("/")
            source_url_list[-1] = re.sub(r"\d+", str(page_num),  source_url_list[-1])
            source_url = "/".join(source_url_list)

            page_url = response.urljoin(source_url)

            # self.proxy_url = get_proxy_url()
            # print("proxy_url add_detail_url_by_parent: %s" % self.proxy_url)

            yield Request(url=page_url, callback=self.parse_detail
                          , headers=response.request.headers)
                        #   , headers=response.request.headers, meta=response.request.meta.update({"proxy": self.proxy_url}))


    def add_detail_url_by_parent(self, select_obj, response):
        """
        添加明细url，通过父页面 
        通过列表页添加 详情页

        :param select_obj:
        :param response:
        :return:
        """
        
        posts_list_div = select_obj.xpath("""//div[@id="J_posts_list"]""")
        detail_page_url_list = posts_list_div.xpath(""".//div[@class="thread_item"]//h3/a/@href""")

        for detail_page_url in detail_page_url_list:
            detail_page_url_compplete = response.urljoin(detail_page_url.extract()).replace(".html", "/1.html")
            yield Request(url=detail_page_url_compplete, callback=self.parse_detail
                          , headers=response.request.headers)
                        #   , headers=response.request.headers, meta=response.request.meta.update({"proxy": self.proxy_url}))


    @staticmethod
    def _get_page_num(select_obj):
        """
        获取页数

        :param select_obj:
        :return:
        """
        # 通过xpath 获取分页器
        split_flag = "::"
        posts_list_div = select_obj.xpath("""//div[@id="J_posts_list"]""")
        page_div = posts_list_div.xpath(""".//div[@class="page"]""")

        # 从分页器获取 页数
        # 获取总篇数
        # 获取每页篇数
        # total_num // page_size 可以整除，页数 = total_num // page_size
        # total_num // page_size 不可以整除，页数 = total_num // page_size +1
        if len(page_div) == 0:
            return 1

        total_num = int(page_div.xpath("""./font/b/text()""").extract_first())
        page_size_str = split_flag.join(page_div.xpath("""./text()""").extract())
        page_size = re.search(r"每页(?P<page_size>\d+).*?" + split_flag, page_size_str, re.S)
        page_size = int(page_size.group("page_size"))
        div, mod = divmod(total_num, page_size)
        
        page_num = div
        if mod > 0:
            page_num += 1

        return page_num


    def parse_data(self, select_obj, response):
        # 解析详情页数据
        # so select_obj
        tr_so_list = select_obj.xpath("""//div[@id="J_posts_list"]//table[@id='ipc']//tbody//tr""")

        page_num = self._get_page_num(select_obj)
        # 通过阈值终止抓取
        if len(self.empty_page_list) <= self.empty_page_threshold:
            self._set_page_total(page_num)

        # 遇到空页面，记录page
        if not len(tr_so_list):
            page_num_match = self.re_compile_proxy_detail.match(response.url)
            page_num_dict = page_num_match.groupdict()
            # page_num = page_num_dict.get("page", "unknown")
            page_num = "_".join(page_num_dict.values())
            
            self.empty_page_list.append(page_num)
        
        for tr_so in tr_so_list:

            "ip	端口号	代理位置	代理类型	验证时间"
            item = Cn66IPItem()
            item_loader = ItemLoader(item=item, selector=tr_so)
            item_loader.default_output_processor = TakeFirst()
            item_loader.add_xpath(Cn66IPItemEnum.ip.value, "./td[position()=1]/text()")
            item_loader.add_xpath(Cn66IPItemEnum.port.value, "./td[position()=2]/text()")
            item_loader.add_xpath(Cn66IPItemEnum.location.value, "./td[position()=3]/text()")
            item_loader.add_xpath(Cn66IPItemEnum.anonymity_type.value, "./td[position()=4]/text()")
            yield item_loader.load_item()
