import random

import pandas as pd

from spider_proxy.spider_model.spider_proxy_model import SpiderProxyModel

csv_data = pd.read_csv("./spider_proxy/spider_common/proxy_data.csv")


def get_proxy_url():
	"""
	返回代理类型 和 代理地址
	:return:
	"""
	
	proxy_line_num = random.randint(0, len(csv_data)-1)
	
	proxy_model = csv_data.loc[proxy_line_num] # type: SpiderProxyModel
	
	return "%s://%s:%s" % (proxy_model.protocol, proxy_model.ip, proxy_model.port)


if __name__ == '__main__':
	pass

