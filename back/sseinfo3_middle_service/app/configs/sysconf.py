import os

from configs.base import PROJECT_NAME
from configs.sse_info3_conf import time_interval
from utils.loader import conf_loader, parse_args

CURR_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(CURR_PATH))

LOG_DIR = os.path.join(PROJECT_PATH, "logs", "")  # 日志文件夹路径

# ######################################## Gunicorn配置  ########################################
LOG_LEVEL = "INFO"  # 影响Gunicorn和Flask的LOGGER
AUTO_RELOAD = parse_args("AUTO_RELOAD", False, bool)  # 设置此项可以让gunicorn检测文件变化并且重启
WORK_NUMS = parse_args("WORKERS_NUMS", 1, int)  # 如果设置为0则自动设置
BIND = conf_loader("BIND", "0.0.0.0:8000")

# ######################################## Flask-JWT配置  ########################################
SSO_LOGIGN = conf_loader('SSO_LOGIGN', True)  # 是否支持单点登录 True:支持，False:不支持
JWT_ACCESS_TOKEN_EXPIRES = conf_loader('JWT_ACCESS_TOKEN_EXPIRES', 60 * 60 * 24)
LOGIN_KEY = conf_loader('LOGIN_KEY', "lk_")

# ###################################### Flasksqlalchemy配置  ####################################
# 是否使用连接池
USE_DB_POOL = parse_args("USE_DB_POOL", True, bool)

# 连接池配置, 如果USE_DB_POOL为false不生效
SQLALCHEMY_ENGINE_OPTIONS = dict(
    pool_size=parse_args("DB_POOL_SIZE", 5, int),  # 链接池数量
    # max_overflow=100,  # 当连接池中链接已经用完了, 最多还允许建立多少额外的链接
    # pool_timeout=5,   # 指定池的连接超时, 秒为单位
    # 连接池回收时间, 过了n秒之后连接池会释放过期链接并创建新链接, 这个值要小于mysql的max_timeout, 否则会lost connection, 默认8小时
    pool_recycle=parse_args("DB_POOL_RECYCLE", 8 * 60, int),
)

MYSQL_USER = conf_loader('MYSQL_USER', 'downfile')
MYSQL_PASSWD = conf_loader('MYSQL_PASSWD', 'datagrand@123')
MYSQL_HOST = conf_loader('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = conf_loader('MYSQL_PORT', 16369)
MYSQL_DATABASE = conf_loader('MYSQL_DATABASE', "test")
MYSQL_CHARSET = conf_loader("MYSQL_CHARSET", "utf8mb4")
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=%s' % (
    MYSQL_USER,
    MYSQL_PASSWD,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE,
    MYSQL_CHARSET,
)

SQLALCHEMY_BINDS_CONTRACT = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=%s' % (
MYSQL_USER,
MYSQL_PASSWD,
MYSQL_HOST,
MYSQL_PORT,
"contract",
MYSQL_CHARSET)

# ######################################## REDIS配置  ########################################
REDIS_CONFIG = {
    "host": conf_loader('REDIS_HOST', 'redis'),
    "port": conf_loader('REDIS_PORT', 6379),
    "passwd": conf_loader('REDIS_PASSWD', ''),
    "db": conf_loader('REDIS_DB', '7'),
}
REDIS_USER_SESSION_PREFIX = "us_"  # user session prefix in redis.
CONF_KEY = "conf_key"  # redis缓存的conf配置key

REDIS_USER_SESSION_TIMEOUT = 7 * 24 * 60 * 60  # user session timeout.
REDIS_CACHING_TIMETOU = 60 * 10
CACHING_KEY_REFIX = "cache_"

USE_REDIS_CACHE = parse_args("USE_REDIS_CACHE", False, bool)

# ############################################## sentry配置  #####################################
# 测试环境的token, 考虑设置为从env中取值
SENTRY_DNS = conf_loader("SENTRY_DNS", "")
SENTRY_ENABLE = parse_args("SENTRY_ENABLE", False, bool)

# #########################################  Mongodb设置  #########################################
MONGODB_CONNECT_URL = None
MONGODB_DB = None


# #########################################  CELERY设置  #########################################
# https://docs.celeryproject.org/en/master/userguide/configuration.html
class CeleryConfig:
    sentinel_flag = False

    if not sentinel_flag:
        broker_url = 'redis://{0}:{1}/{2}'.format(
            REDIS_CONFIG["host"],
            REDIS_CONFIG["port"],
            conf_loader("CELERY_REDIS_DB", 0),
        )

        result_backend = "redis://{0}:{1}/{2}".format(
            REDIS_CONFIG["host"],
            REDIS_CONFIG["port"],
            conf_loader("CELERY_REDIS_RESULT_DB", 1),
        )

        broker_transport_options = {
            'max_retries': 10,
            'interval_start': 0,
            'interval_step': 1,
            'interval_max': 1
        }

    else:
        sentinel_lists = [("redis_sentinel", "26379")]
        sentinel_password = '123456'
        broker_url = ''
        result_backend = ''
        for sentinel in sentinel_lists:
            broker_url += f'sentinel://:{sentinel_password}@{sentinel[0]}:{sentinel[1]};'
            result_backend += f'sentinel://:{sentinel_password}@{sentinel[0]}:{sentinel[1]};'

        broker_transport_options = {
            'max_retries': 10,
            'interval_start': 0,
            'interval_step': 1,
            'interval_max': 1,
            'master_name': 'mymaster'
        }
        result_backend_transport_options = {
            'master_name': 'mymaster'
        }

    imports = [
        # "tasks.send_overtime_message",
        "tasks.data_input_task",
        "tasks.data_output_task"
    ]

    timezone = "Asia/Shanghai"
    enable_utc = False
    worker_max_tasks_per_child = 100
    task_soft_time_limit = 600
    task_default_queue = "main_queue"
    worker_concurrency = parse_args("CELERY_WORKER_CONCURRENCY", 2, int)
    beat_schedule = {
        # "data_input_task": {
        #     "task": "tasks.data_input_task.data_input",
        #     "schedule": 60 * 30,  # 秒
        #     "args": ()
        # },
        "push_kafka_task": {
            "task": "tasks.data_output_task.push_kafka",
            "schedule": 60 * time_interval,  # 秒
            "args": ()
        },
    }

MAX_PAGE_SIZE = 9999




