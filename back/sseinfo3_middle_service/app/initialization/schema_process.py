# -*- coding: utf-8 -*-

# 使用你喜欢的验证工具, 在这里注册验证的错误

from marshmallow.exceptions import ValidationError

import utils.custom_response as ucr
from . import app


@app.errorhandler(ValidationError)
def validate_error(validate_error: ValidationError):
    """处理Schema带来的报错"""
    return ucr.op_fail(validate_error.messages, status=400), 400
