from flask import Flask

from configs import base

app: Flask


def _init_custom():
    """
    非强制导入, 使用到就打开注释
    """
    from . import (  # 这里开始, 选择性导入;
        # sentry_process,; session_process,; mongodb_process,; permission_process, jwtextend_process
        restful_process, redis_process, schema_process, service_process)


def _init():
    """
    初始化所有APP的配置, 导入自己所需要使用的功能, 一些初始化必须要的, 不可以删掉
    """
    from . import logger_process, command_process, exception_process, request_process, sqlalchemy_process


def create_app() -> Flask:
    global app

    app = Flask(base.PROJECT_NAME)
    _init()
    _init_custom()
    from . import blueprint_process  # 最后导入蓝图

    return app
