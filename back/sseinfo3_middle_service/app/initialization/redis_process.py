#! /usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2019年2月13日

@author: ljbai
'''

from configs import sysconf
from databases.redisdb import create_default_redis
from . import app

logger = app.logger


try:
    redis_cli = create_default_redis(sysconf.REDIS_CONFIG)
    app.extensions["redis_cli"] = redis_cli
except Exception as e:
    logger.error("Redis init fail...")
    logger.exception(e)
    raise e
