import os


# db config
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_DATABASE = os.environ.get("DB_PORT", "spider")
DB_USER = os.environ.get("DB_PORT", "spider_user")
DB_PASSWD = os.environ.get("DB_PORT", "123456")
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
MQ_HOST = os.environ.get("MQ_HOST", "127.0.0.1")
MQ_PORT = os.environ.get("MQ_PORT", "5672")
MQ_EXCHANGE = os.environ.get("MQ_EXCHANGE", "spider")
MQ_VIRTUAL_HOST = os.environ.get("MQ_VIRTUAL_HOST", "/spider")

MQ_CONFIG = {'host': MQ_HOST,
          'port': MQ_PORT,
          'exchange': MQ_EXCHANGE,
          "virtual_host": MQ_VIRTUAL_HOST,
      }

PRODUCER_TOPIC = os.environ.get("PRODUCER_TOPIC", "new_proxy_data")
