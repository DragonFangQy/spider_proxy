from scrapy.cmdline import execute
import os
import sys

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # execute(['scrapy','crawl','com_zdaye']) # Test
    execute(['scrapy','crawl','cn_66ip'])
