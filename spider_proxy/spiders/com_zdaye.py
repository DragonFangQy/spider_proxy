import re
import datetime

import scrapy
from scrapy import Request, Selector
from scrapy.http import HtmlResponse

# from spider_proxy.utils.utils_proxy import get_proxy_url

"""
站大爷代理
"""
class ComZdayeSpider(scrapy.Spider):
    name = 'com_zdaye'
    allowed_domains = ['zdaye.com']
    # start_urls = ['http://zdaye.com/']

    page_total = [1, 2, 3, 4, 5]
    url_format = "https://www.zdaye.com/dayProxy/{year}/{month}/{page}.html"

    init_page_total = False

    diff_month = 1

    proxy_url = None
	
    def start_requests(self):

        # 当前月份
        current_datetime = datetime.datetime.now()

        for i in range(self.diff_month):

            current_datetime_list = current_datetime.strftime("%Y-%m").split("-")

            for page in self.page_total:
                print("月份 %s,page_total：%s,当前 page：%s" % (current_datetime.month, self.page_total, page))
                yield Request(url=self.url_format.format(year=current_datetime_list[0], month=current_datetime_list[1], page=page + 1))

            # 上个月
            pre_month_datetime = datetime.date(current_datetime.year, current_datetime.month, 1) + datetime.timedelta(days=-1)
            current_datetime = datetime.date(pre_month_datetime.year, pre_month_datetime.month, 1)

    def parse(self, response: HtmlResponse, **kwargs):

        select_obj = Selector(response)

        page_num = self._get_page_num(select_obj)
        self._set_page_total(page_num)

        yield from self.add_detail_url_by_parent(select_obj, response)
        # self.add_detail_url_by_parent(select_obj, response)

    def parse_detail(self, response: HtmlResponse, **kwargs):

        select_obj = Selector(response)

        # self.add_detail_url_by_brother(response, select_obj)
        yield from self.add_detail_url_by_brother(response, select_obj)

    def add_detail_url_by_brother(self, response, select_obj):
        """
        添加明细url，通过同胞页面（通过本页的页面选择器添加）

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

            self.proxy_url = get_proxy_url()
            print("proxy_url add_detail_url_by_parent: %s" % self.proxy_url)

            yield Request(url=page_url, callback=self.parse_detail
                          , headers=response.request.headers, meta=response.request.meta.update({"proxy": self.proxy_url}))

    def add_detail_url_by_parent(self, select_obj, response):
        """
        添加明细url，通过父页面

        :param select_obj:
        :param response:
        :return:
        """

        posts_list_div = select_obj.xpath("""//div[@id="J_posts_list"]""")
        detail_page_url_list = posts_list_div.xpath(""".//div[@class="thread_item"]//h3/a/@href""")

        self.proxy_url = get_proxy_url()
        print("proxy_url add_detail_url_by_parent: %s" % self.proxy_url)
        
        for detail_page_url in detail_page_url_list:
            detail_page_url_compplete = response.urljoin(detail_page_url.extract()).replace(".html", "/1.html")
            yield Request(url=detail_page_url_compplete, callback=self.parse_detail
                          , headers=response.request.headers, meta=response.request.meta.update({"proxy": self.proxy_url}))

    def _set_page_total(self, page_num):
        for page in range(1, page_num + 1):
            if page not in self.page_total:
                self.page_total.append(page)

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
        total_num = int(page_div.xpath("""./font/b/text()""").extract_first())
        page_size_str = split_flag.join(page_div.xpath("""./text()""").extract())
        page_size = re.search(r"每页(?P<page_size>\d+).*?" + split_flag, page_size_str)
        page_size = int(page_size.group("page_size"))
        page_num = total_num // page_size
        if total_num % page_size != 0:
            page_num += 1

        return page_num
