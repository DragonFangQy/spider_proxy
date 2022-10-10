from enum import Enum
import scrapy
from scrapy.loader.processors import TakeFirst
# from itemloaders.processors import TakeFirst

class Cn66IPItemEnum(Enum):
    protocol = "protocol"
    ip = "ip"
    port = "port"
    anonymity_type = "anonymity_type"
    location = "location"
    network_operator = "network_operator"


class Cn66IPItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    default_output_processor = TakeFirst()
    protocol = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
    anonymity_type = scrapy.Field()
    location = scrapy.Field()
    network_operator = scrapy.Field()
