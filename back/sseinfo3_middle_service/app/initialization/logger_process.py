"""
Created on 2019年1月14日
@author: ljbai

comment by LuShuYang:
    Flask的log分为两个部分, 一个是在业务代码里面使用的app.logger, 一个是werkzueg的logger,

    在本地的时候我们将werkzueg的logger和app.logger重定向到标注输出中,

    如果在部署的时候, 使用gunicorn部署, 再将gunicorn的logger和app的logger都重定向到File中.

    因此不修改werkzeug的logger, 且不要使用werkzueg进行部署.
"""
import logging
import os
import sys
import traceback
from logging.handlers import TimedRotatingFileHandler

from configs import sysconf
from configs.base import PROJECT_NAME
from configs.sysconf import LOG_LEVEL

logger = logging.getLogger(PROJECT_NAME)  # same as app.logger
logger.setLevel(LOG_LEVEL)


formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s:%(lineno)s %(funcName)s %(message)s')


file_name = os.path.join(sysconf.LOG_DIR, "log.log")

rh = TimedRotatingFileHandler(file_name, when='D', interval=1, backupCount=30)
#TimedRotatingFileHandler对象⾃定义⽇志级别
rh.setLevel(logging.DEBUG)
#TimedRotatingFileHandler对象⾃定义⽇志级别
rh.suffix = "%Y_%m_%d"
#TimedRotatingFileHandler对象⾃定义⽇志格式
rh.setFormatter(formatter)
logger.addHandler(rh)  #logger⽇志对象加载TimedRotatingFileHandler对象

#创建StreamHandler对象
sh = logging.StreamHandler()
#StreamHandler对象⾃定义⽇志级别
sh.setLevel(logging.DEBUG)
#StreamHandler对象⾃定义⽇志格式
sh.setFormatter(formatter)
logger.addHandler(sh)  #logger⽇志对象加载StreamHandler对象


for handler in logger.handlers:
    handler.formatter = formatter

def logger_exception():
    exc_type, exc_value, exc_traceback = sys.exc_info()

    error_line = []
    for item in traceback.StackSummary.from_list(traceback.extract_tb(exc_traceback)).format():
        error_line.append(item)

    logger.error("%s: %s" % (exc_type, exc_value))
    logger.error("".join(error_line))
