
import json
from sqlalchemy import Column, String, Integer

from spider_proxy.spider_model.base_model import BaseModel


class SpiderProxyModel(BaseModel):
	__tablename__ = "spider_proxy"

	protocol = Column(String(100), default="http", nullable=False, comment="类型：http https socks ")
	ip = Column(String(100), nullable=False, comment="ip")
	port = Column(String(100), nullable=False, comment="端口")
	anonymity_type = Column(String(100), default="", nullable=False, comment="匿名类型：透明 匿名 高匿")
	location = Column(String(100), default="", nullable=False, comment="位置(归属地)")
	network_operator = Column(String(100), default="", nullable=False, comment="网络运营商")
	useable = Column(Integer, default=1, nullable=False, comment="是否可用")
	telnet_num_1 = Column(Integer, default=0, nullable=False, comment="telnet 次数")
	telnet_num_0 = Column(Integer, default=0, nullable=False, comment="telnet 次数")
	total_seconds = Column(Integer, default=0, nullable=False, comment="耗时 毫秒", server_default="0")

	def __init__(self, ip, port, protocol="http", location="", anonymity_type="", network_operator="", useable=1):
		self.protocol = protocol
		self.ip = ip
		self.port = port
		self.anonymity_type = anonymity_type
		self.location = location
		self.network_operator = network_operator
		self.useable = useable

	def to_string(self):
		return json.dumps(self.to_dict(), ensure_ascii=False)

	def to_dict(self):
		return {
			"protocol":self.protocol,
			"ip":self.ip,
			"port":self.port,
			"anonymity_type":self.anonymity_type,
			"location":self.location,
			"network_operator":self.network_operator,
			"useable":self.useable,
		}



