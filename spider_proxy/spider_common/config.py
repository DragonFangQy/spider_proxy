
# db config
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_DATABASE = "spider"
DB_USER = "spider_user"
DB_PASSWD = "123456"
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
MQ_HOST = "127.0.0.1"
MQ_PORT = 5672
MQ_EXCHANGE = "spider"
MQ_VIRTUAL_HOST = "/spider"

MQ_CONFIG = {'host': MQ_HOST,
          'port': MQ_PORT,
          'exchange': MQ_EXCHANGE,
          "virtual_host": MQ_VIRTUAL_HOST,
      }

PRODUCER_TOPIC = "new_proxy_data"
