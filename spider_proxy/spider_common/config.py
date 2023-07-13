import os


# db config
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_DATABASE = os.environ.get("DB_DATABASE", "spider")
DB_USER = os.environ.get("DB_USER", "spider_user")
DB_PASSWD = os.environ.get("DB_PASSWD", "123456")
"""
Microsoft SQL Sever	mssql+pymssql://usename:[email protected]:port/dbname
MySql	mysql+pymysql://username:[email protected]:port/dbname?charset=%s
Oracle	cx_Oracle://username:[email protected]:port/dbname
PostgreSQL	postgresql://username:[email protected]:port/dbname
SQLite	sqlite://file_path 
"""
SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%s/%s' % (
    DB_USER,
    DB_PASSWD,
    DB_HOST,
    DB_PORT,
    DB_DATABASE
)


# MQ config   
# account   guest
# pwd       guest
MQ_HOST = os.environ.get("MQ_HOST", "127.0.0.1")
MQ_PORT = os.environ.get("MQ_PORT", "5672")
MQ_USER = os.environ.get("MQ_USER", "spider_user")
MQ_PWD = os.environ.get("MQ_PWD", "123456")
MQ_EXCHANGE = os.environ.get("MQ_EXCHANGE", "spider")
MQ_VIRTUAL_HOST = os.environ.get("MQ_VIRTUAL_HOST", "/spider")

MQ_CONFIG = {'host': MQ_HOST,
          'port': MQ_PORT,
          'exchange': MQ_EXCHANGE,
          "virtual_host": MQ_VIRTUAL_HOST,
          "user": MQ_USER,
          "pwd": MQ_PWD,
      }

PRODUCER_TOPIC = os.environ.get("MQ_PRODUCER_TOPIC", "new_proxy_data")


LOG_LEVEL = os.environ.get("CONF_LOG_LEVEL", "INFO")


CONCURRENT_REQUESTS = int(os.environ.get("CONF_CONCURRENT_REQUESTS", "3"))
DOWNLOAD_DELAY = int(os.environ.get("CONF_DOWNLOAD_DELAY", "3"))
AUTOTHROTTLE_START_DELAY = int(os.environ.get("CONF_AUTOTHROTTLE_START_DELAY", "3"))
AUTOTHROTTLE_MAX_DELAY = int(os.environ.get("CONF_AUTOTHROTTLE_MAX_DELAY", "10"))
INIT_PAGE_SIZE = int(os.environ.get("CONF_INIT_PAGE_SIZE", "5"))
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.environ.get("CONF_CONCURRENT_REQUESTS_PER_DOMAIN", "10"))


"""
    Kafka Config
"""
KAFKA_BROKER = os.environ.get("CONF_KAFKA_BROKER", "8.218.227.109:9095")
KAFKA_TOPIC = os.environ.get("CONF_KAFKA_TOPIC", "spider_topic")
KAFKA_TOPIC = os.environ.get("CONF_KAFKA_TOPIC", "test_topic")
KAFKA_GROUP = os.environ.get("CONF_KAFKA_CONSUMER_GROUP", "test_topic_consumer_group_0001")
KAFKA_POLL_TIMEOUT = int(os.environ.get("CONF_KAFKA_POLL_TIMEOUT", "5"))
KAFKA_POLL_NONE_SLEEP = int(os.environ.get("CONF_POLL_NONE_SLEEP", "5"))

# # kafka 每生产 100 次消息，log 一次
KAFKA_LOGS_ONCE = int(os.environ.get("CONF_KAFKA_LOGS_ONCE", "10000"))

KAFKA_PRODUCER_CONF = { 
    "bootstrap.servers": KAFKA_BROKER,
    "compression.type":"gzip", 
    "security.protocol": "PLAINTEXT",
}

KAFKA_CONSUMER_CONF = { 
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": KAFKA_GROUP,
    "session.timeout.ms": 6000,
    "auto.offset.reset": "earliest",
    "enable.auto.offset.store": False, 
}
 


