#! /usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2020年02月07日

@author: jianzhihua
'''

from typing import Any

from flask import request
from flask_jwt_extended import JWTManager as _JWTManager
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

import utils.custom_response as ucr
from configs.base import SECRET_KEY
from configs.sysconf import JWT_ACCESS_TOKEN_EXPIRES
from . import app

app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES


class JWTManager(_JWTManager):

    def _set_error_handler_callbacks(self, app):
        """
        暂停注册错误, 由exception_process统一处理
        """
        ...


class AnonymousUser:
    """
    有别于登录的用户
    """

    is_superuser = False
    is_anonymous = True

    def __getattribute__(self, name: str) -> Any:
        if name in ('is_superuser', "is_anonymous"):
            return super().__getattribute__(name)
        return None


jwt = JWTManager(app)


@jwt.user_loader_callback_loader
def user_loader_callback(identity: dict):
    from blueprints.users.user_models import UserModel

    user_id = identity.get("user_id")
    if not user_id:
        raise JWTExtendedException("Invalid Token!")

    return UserModel.active_query.filter_by(id=user_id).first() or AnonymousUser()


@app.before_request
def jwt_auth():
    """
    在登录前验证接口中的jwt token是否有效
    """
    if request.args.get("is_debug") == "is_debug":
        return

    # 跳过一些验证..
    if (request.path, request.method) in frozenset({
        ("/api/login", "POST"),
        ("/api/register", "POST"),
    }):
        return

    verify_jwt_in_request()


@app.errorhandler(JWTExtendedException)
def no_auth_handler(error: JWTExtendedException):
    """
    @attention: 提示
    """
    return ucr.op_fail(str(error), status=401), 401
