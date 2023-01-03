#!/usr/bin/env python
import os
import sys

path_str = os.path.dirname( os.path.dirname( os.path.abspath(__file__)))

sys.path.insert(1, path_str)
sys.path.insert(2, path_str+"/spider_proxy")

from migrate.versioning.shell import main
from spider_proxy.spider_common.config import SQLALCHEMY_DATABASE_URI


if __name__ == '__main__':
    main(url=SQLALCHEMY_DATABASE_URI,repository="./",debug='False')
