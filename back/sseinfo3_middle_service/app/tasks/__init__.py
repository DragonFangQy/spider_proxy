import logging
import os

from celery import Celery, Task, platforms
from celery.signals import after_setup_logger
from dg_logging.templates.config_dicts import MultiprocessSafeTimedRotatingFileHandler
from flask import Flask

from configs import sysconf as configs


@after_setup_logger.connect
def setup_loggers(logger: logging.Logger, *args, **kwargs):
    """重写Logger的handler"""
    # redirect workers log to file
    worker_log_format = "%(asctime)s - %(process)d - %(thread)d - %(levelname)s - %(filename)s:%(lineno)s"\
                        " - %(funcName)s - %(message)s"
    formatter = logging.Formatter(worker_log_format)

    handler = MultiprocessSafeTimedRotatingFileHandler(os.path.join(configs.LOG_DIR, "celery.log"),
                                                       when="d",
                                                       backupCount=10)
    handler.formatter = formatter
    logger.setLevel(configs.LOG_LEVEL)
    logger.handlers.append(handler)


def make_celery(app: Flask):
    # make sure task running under flask context

    class ContextTask(Task):

        abstract = True

        def __call__(self, *args, **kwargs):
            """Execute task."""
            with app.app_context():
                return Task.__call__(self, *args, **kwargs)

    platforms.C_FORCE_ROOT = True
    celery_app = Celery(configs.PROJECT_NAME, task_cls=ContextTask)
    celery_app.config_from_object(configs.CeleryConfig)

    return celery_app
