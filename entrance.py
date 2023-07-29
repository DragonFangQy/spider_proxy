import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == '__main__':

    counter = 0

    time.sleep(15)
    while True:
        try:

            settings = get_project_settings()

            crawler = CrawlerProcess(settings)

            # crawler.crawl('com_zdaye')
            crawler.crawl('cn_66ip')
            crawler.crawl('cn_89ip')
            crawler.crawl('com_seofangfa') 
            crawler.crawl('com_zdaye') 

            crawler.start()
        
        except Exception as e:
            import traceback
            traceback.print_exc()

        counter+=1
        print("=="*10)
        print("\n\n")
        print(f"counter: {counter}")
        time.sleep(3600)
        print("\n\n")
        print("=="*10)

 