"""
Created on 2018年11月27日

@author: ljbai
"""

from flask import request

import utils.custom_response as ucr
from initialization.logger_process import logger
from utils.exceptions import NoAuthResponse, NoPermission, ParamResponse, RedirectResponse, TipResponse
from . import app


@app.errorhandler(RedirectResponse)
def redirect_handler(error: RedirectResponse):
    """
    @attention: 重定向
    """
    curl = error.show()
    return ucr.op_redirect(curl)


@app.errorhandler(TipResponse)
def tip_handler(error: TipResponse):
    """
    @attention: 提示
    """
    msg = error.show()
    return ucr.op_fail(msg)


@app.errorhandler(ParamResponse)
def param_handler(error: ParamResponse):
    """
    @attention: 带参数提示
    """
    msg, data = error.show()
    return ucr.op_fail(msg, data), 400


@app.errorhandler(NoAuthResponse)
def no_auth_response(error: NoAuthResponse):
    """
    处理登录发生的错误
    """
    return ucr.op_fail(error.msg, dict(), 401), 401


@app.errorhandler(NoPermission)
def no_permission_response(error: NoPermission):
    """
    权限相关错误
    """
    return ucr.op_fail("无权限", dict(), 403), 403


@app.errorhandler(404)
def c_404_handler(error):
    """
    @attention: 404服务器警告异常
    """
    # msg,data = error.show()
    return ucr.op_fail(message='Resource Not Found Error!', data={}, status=404), 404


@app.errorhandler(400)
def c_400_handler(error):
    """
    @attention: 400服务器警告异常
    """
    # msg,data = error.show()
    return ucr.op_fail(message='Bad request!', data={}, status=400), 400


@app.errorhandler(405)
def c_405_handler(error):
    """
    @attention: 405服务器警告异常
    """
    # msg,data = error.show()
    return ucr.op_fail(message='The method is not allowed for the requested URL!', data={}, status=405), 405


@app.errorhandler(500)
def c_500_handler(error):
    """
    @attention: 500服务器警告异常
    """
    # msg,data = error.show()
    # return ucr.op_fail(msg='System Error!', data={}, status=500)
    return ucr.op_fail(message='System Error!', data={}, status=500)


@app.errorhandler(Exception)
def base_handler(error):
    """
    @attention: 未知异常
    """
    url_data = "url(%s):%s" % (request.url, request.method)
    get_data = "get_data:%s" % dict(request.args)
    json_data = "json_data:%s" % request.params
    log_msg = "\n".join([url_data, get_data, json_data])
    logger.error(log_msg)
    logger.exception(error)
    msg = "系统繁忙，请稍后再试!"
    return ucr.op_fail(msg, status=500)
