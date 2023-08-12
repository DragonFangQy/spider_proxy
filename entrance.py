import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spider_proxy.spider_common import config
from spider_proxy.utils.utils_log import my_logger

if __name__ == '__main__':

    counter = 0

    time.sleep(config.START_TIME_SLEEP)
    while True:
        try:
            settings = get_project_settings()

            crawler = CrawlerProcess(settings)

            crawler.crawl('cn_66ip')
            crawler.crawl('cn_89ip')
            crawler.crawl('com_seofangfa') 
            crawler.crawl('com_zdaye') 

            crawler.start()
        
        except Exception as e:
            import traceback
            traceback.print_exc()

        counter+=1
        my_logger.info("=="*10)
        my_logger.info("\n\n")
        my_logger.info(f"counter: {counter}")
        time.sleep(3600)
        my_logger.info("\n\n")
        my_logger.info("=="*10)

 