# from scrapy.cmdline import execute
# import os
# import sys

# if __name__ == '__main__':
#     sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#     # execute(['scrapy','crawl','com_zdaye']) # Test
#     execute(['scrapy','crawl','cn_66ip'])
#     # execute(['scrapy','crawl','cn_89ip'])




from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == '__main__':
    settings = get_project_settings()

    crawler = CrawlerProcess(settings)

    # crawler.crawl('com_zdaye')
    crawler.crawl('cn_66ip')
    crawler.crawl('cn_89ip')

    crawler.start()
