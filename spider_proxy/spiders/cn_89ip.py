import scrapy
from scrapy import Request, Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from spider_proxy.spider_items.cn_66ip_item import Cn66IPItem, Cn66IPItemEnum


class Cn89ipSpider(scrapy.Spider):
    name = 'cn_89ip'
    allowed_domains = ['89ip.cn']
    # start_urls = ['http://89ip.cn/']

    page_total = [1, 2]
    url_format = "http://www.89ip.cn/index_{page}.html"

    init_page_total = False

    def start_requests(self):
        for page in self.page_total:
            print("page_total：%s,当前 page：%s" % (len(self.page_total), page))
            yield Request(url=self.url_format.format(page=page))

    def parse(self, response):

        select_obj = Selector(response, type="html")

        page_num = self._get_page_num(select_obj)
        self._set_page_total(page_num)

        # 找到页面中的表格，从表格中获取数据
        tr_so_list = select_obj.xpath("""//div[@class="layui-col-md8"] //table[@class='layui-table']//tr[position()>1]""")

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

    @staticmethod
    def _get_page_num(select_obj):
        """
        获取页数

        :param select_obj:
        :return:
        """

        # 从分页器获取 最后五个分页器（实际上2个基本就够用了），
        # 3 4 。。。。18 19 最后一页 ；这种情况 19 才是我们要的页码，最后一页只是一个按钮
        page_num_so_list = select_obj.xpath("//div[@class='layui-row layui-col-space15']//div[@id='layui-laypage-1']/a[position()>last()-5]")

        page_num_list = []
        for page_num_so in page_num_so_list:
            try:
                page_num_list.append(int(page_num_so.xpath("./text()").extract_first()))
            except Exception as e:
                continue
        page_num = 1
        if len(page_num_list) > 1:
            page_num = page_num_list[-1]
        return page_num

    def _set_page_total(self, page_num):
        for page in range(1, page_num + 1):
            if page not in self.page_total:
                self.page_total.append(page)
