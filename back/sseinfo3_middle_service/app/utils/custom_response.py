"""
Created on 2018年11月27日

@author: ljbai

@attention: 响应前端固定格式，当前采用业务异常都返回200的方式，结构为
{
    status: 状态码(0:操作成功, 1, 2: 业务异常提示,3:重定向),支持自定义status,
    data: 响应参数(结构建议是字典),
    message: 提示信息(一般在业务异常时使用,如果是重定向,则为重定向url地址)
}

"""
from flask import jsonify, request


def op_success(data="", status=0, message='Success!'):
    """
    @attention: 操作成功
    """
    res = {"status": status, "message": message, "data": data, "request_id": request.request_id}
    return jsonify(res)


def op_fail(message, data="", status=None):
    """
    @attention: 操作失败
    @note: 带data参数情况下,返回2;常规提示,返回1
    """
    data = data if data else {}
    data_status = 2 if data else 1
    status = status if status is not None else data_status
    res = {"status": status, "message": message, "data": data, "request_id": request.request_id}
    return jsonify(res)


def op_redirect(url):
    """
    @attention: 重定向 PS:目前默认重定向为登录页面，由前端实现
    """
    return op_fail('Redirect!', status=301, data=url)


Response = op_success
