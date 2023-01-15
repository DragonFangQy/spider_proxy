# -*- coding: utf-8 -*-
from initialization.logger_process import logger
from libs import set_logger, ServiceException
from utils.custom_response import op_fail
from . import app

set_logger(logger)


@app.errorhandler(ServiceException)
def service_exception(e: ServiceException):
    return op_fail(message=f"third party service is unavailable right now, error: {e}")
