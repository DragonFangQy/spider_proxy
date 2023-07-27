import random

import pandas as pd
from spider_proxy.spider_common import config

from spider_proxy.utils.utils_db import db_session
from spider_proxy.spider_model.spider_proxy_model import SpiderProxyModel

csv_data = pd.read_csv("./spider_proxy/spider_common/proxy_data.csv")

use_count = 0
useable_1_list = db_session.query(SpiderProxyModel).filter(SpiderProxyModel.useable == 1).order_by(SpiderProxyModel.update_time).limit(config.PROXY_NUM).all()

def get_proxy_url():
	"""
	返回代理类型 和 代理地址
	:return:
	"""
	
	proxy_line_num = random.randint(0, len(useable_1_list)-1)
	
	proxy_model = csv_data.loc[proxy_line_num] # type: SpiderProxyModel
	
	use_count +=1
	if use_count == config.REFRESH_PROXY_NUM or not useable_1_list:
		useable_1_list = db_session.query(SpiderProxyModel).filter(SpiderProxyModel.useable == 1).order_by(SpiderProxyModel.update_time).limit(config.PROXY_NUM).all()
	
	return "%s://%s:%s" % (proxy_model.protocol, proxy_model.ip, proxy_model.port)


if __name__ == '__main__':
	pass

