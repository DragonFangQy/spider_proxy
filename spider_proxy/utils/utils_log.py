"""
首先，要区分 info 和 finfo
info 是 LOG_LEVEL
finfo 是 file path


# log 所在位置
CONF_LOG_PATH   

# 默认等级
CONF_LOG_LEVEL  

# 只输出控制台，默认 false
CONF_LOG_ONLY_CONSOLE   

# finfo 中看不见 debug，默认为 True。如果为True，即使 LOG_LEVEL == debug 也看不见。
# 这里的 info 说的是 info file，而不是 LOG_LEVEL
CONF_LOG_FINFO_NOT_LOOK_DEBUG    

# file name，默认为 service.log
CONF_LOG_FILE_NAME
"""


import inspect
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import re
import sys
import time
import colorlog


from  os import getenv 
from  os.path import dirname, join

# log的根目录（项目目录），当前文件目录的上上级
log_root_dir = dirname(dirname( dirname(__file__) ))

LOG_PATH = getenv("CONF_LOG_PATH", join(log_root_dir,"logs"))
LOG_LEVEL = getenv("CONF_LOG_LEVEL", logging._levelToName.get(logging.INFO))
LOG_FILE_NAME = getenv("CONF_LOG_FILE_NAME", "service.log")
LOG_ONLY_CONSOLE = False if getenv("CONF_LOG_ONLY_CONSOLE", "False").lower() == "False".lower() else True
LOG_FINFO_NOT_LOOK_DEBUG = True if  getenv("CONF_LOG_FINFO_NOT_LOOK_DEBUG", "True").lower() == "True".lower() else False
LOG_ONLY_CONSOLE
LOG_FINFO_NOT_LOOK_DEBUG
### 日志 ###
# 定义不同日志等级颜色
log_colors_config = {
   'DEBUG': 'bold_cyan',
   'INFO': 'bold_green',
   'WARNING': 'bold_yellow',
   'ERROR': 'bold_red',
   'CRITICAL': 'bold_purple',
}

color_fmt_list = [
    '    %(log_color)s %(levelname)1.1s %(asctime)s %(reset)s',
    '    %(bold_white)s %(name)-8s %(reset)s',
    '    %(message_level_log_color)s    %(levelname)-8s %(reset)s',
    '    %(message_log_color)s %(message)s %(reset)s\n',
]

LOG_FORMATTER = colorlog.ColoredFormatter(
            "\n".join(color_fmt_list),
            reset=True,
            log_colors=log_colors_config,
            secondary_log_colors={
                    'message_level': {
                        'DEBUG': 'bg_bold_cyan',
                        'INFO': 'bg_bold_green',
                        'WARNING': 'bg_bold_yellow',
                        'ERROR': 'bg_bold_red',
                        'CRITICAL': 'bg_bold_purple'
                    },
                    'message': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'purple'
                    }
            },
            style='%'
        ) 

# 必须包含 logging.INFO
LOG_INFO = {
    logging.DEBUG: {
            "log_folder": join(LOG_PATH,"debug"),
            "log_formatter": LOG_FORMATTER,
            "log_handler_class": TimedRotatingFileHandler,
            "log_handler_params": {
                "filename": join(LOG_PATH,"debug", LOG_FILE_NAME), 
                "when": "MIDNIGHT", 
                "interval": 1,
                "backupCount": 30,
                "encoding":"utf-8",
            },
        },
    logging.INFO: {
            "log_folder": join(LOG_PATH,"info"),
            "log_formatter": LOG_FORMATTER,
            "log_handler_class": TimedRotatingFileHandler,
            "log_handler_params": {
                "filename": join(LOG_PATH,"info", LOG_FILE_NAME), 
                "when": "MIDNIGHT", 
                "interval": 1,
                "backupCount": 30,
                "encoding":"utf-8",
            }, 
        },
    logging.WARNING: {
            "log_folder": join(LOG_PATH,"warning"),
            "log_formatter": LOG_FORMATTER,
            "log_handler_class": TimedRotatingFileHandler,
            "log_handler_params": {
                "filename": join(LOG_PATH,"warning", LOG_FILE_NAME), 
                "when": "MIDNIGHT", 
                "interval": 1,
                "backupCount": 30,
                "encoding":"utf-8",
            },
        },
    logging.ERROR: {
            "log_folder": join(LOG_PATH,"error"),
            "log_formatter": LOG_FORMATTER,
            "log_handler_class": TimedRotatingFileHandler,
            "log_handler_params": {
                "filename": join(LOG_PATH,"error", LOG_FILE_NAME), 
                "when": "MIDNIGHT", 
                "interval": 1,
                "backupCount": 30,
                "encoding":"utf-8",
            },
        },
}


class MyLogging(object):
    def __init__(self, level):

        if logging.INFO not in LOG_INFO.keys():
            raise ValueError("level_log_path 必须包含 logging.INFO ")

        self._level = level
        # 创建目录
        self._make_log_folder()
        # 创建 logger
        self._logger_dict = self._create_loggers()

        # CRITICAL = 50
        # FATAL = CRITICAL
        # ERROR = 40
        # WARNING = 30
        # WARN = WARNING
        # INFO = 20
        # DEBUG = 10
        # NOTSET = 0
        # mapping
        self.log_dict = {
            logging.DEBUG: self.debug,
            logging.INFO: self.info,
            logging.WARNING: self.warning,
            logging.ERROR: self.error,
            logging.CRITICAL: self.critical,
        }

    
    def _make_log_folder(self): 

        for level_info in LOG_INFO.values():
            log_folder = level_info.get("log_folder")
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)
        return log_folder

    def _create_loggers(self):
        logger_dict = {}

        log_info_info = LOG_INFO[logging.INFO]

        for level in logging._levelToName.keys():
            is_default = False
            if level == logging.NOTSET:
                continue
            
            # 获取 level_info， 默认使用 INFO 的 level_info
            level_info = LOG_INFO.get(level, None)
            if level_info is None: 
                is_default = True
                level_info = LOG_INFO.get(logging.INFO)

            logger = logger_dict.get(level,logging.getLogger(f"LOGGING_{logging._levelToName.get(level)}"))
            logger.propagate = False
            logger.parent = None
            
            # 先增加 控制台输出
            self._add_console_handler(logger, logger_dict, level, level_info)

            # 如果只输出到控制台，则 continue
            if LOG_ONLY_CONSOLE:
                continue

            # 再增加 info，每个 level 都应该包含 info
            self._add_log_handler(logger, logger_dict, level, log_info_info, logging.INFO)

            if level == logging.INFO or is_default:
                # info 只需要 info handler
                # is_default 如果使用了默认值，说明没有 level handler 对应的自定义配置，所以不再添加 level handler
                continue
            
            # 再增加 level handler
            self._add_log_handler(logger, logger_dict, level, level_info)

        return logger_dict

    def _add_log_handler(self, logger, logger_dict, level, log_info, flevel=None):

        if not flevel:
            flevel = level

        if level == logging.DEBUG and flevel == logging.INFO and LOG_FINFO_NOT_LOOK_DEBUG:
            # finfo 中看不见 debug，默认为 True
            return

        # 创建 handler
        log_handler_class = log_info.get("log_handler_class")
        log_handler_params = log_info.get("log_handler_params")
        log_handler = log_handler_class(**log_handler_params)

        log_formatter = log_info.get("log_formatter")

        if not isinstance(log_handler, logging.Handler):
            raise ValueError(f"{log_handler} not isinstance logging.Handler ")

        log_handler.setFormatter(log_formatter) 
        log_handler.setLevel(level)
        logger.addHandler(log_handler)
        logger_dict.update({level: logger})

    def _add_console_handler(self, logger, logger_dict, level, log_info): 

        if level == logging.DEBUG and self._level > level:
            # 如果指定 level 大于 DEBUG
            # 则 DEBUG 不输出到控制台
            return
        
        log_formatter = log_info.get("log_formatter")

        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(level=level)
        
        logger.addHandler(console_handler)
        logger_dict.update({level: logger})
    
    def _fix_stack_info(self, level, message):
        """
        由于log 实在本类中打印的所以 log 本身的 filename, lineNo, functionName 存在错误
        通过本方法进行修复
        """
        frame = inspect.currentframe()
        co_filename, f_lineno, f_name = frame.f_back.f_back.f_code.co_filename, frame.f_back.f_back.f_lineno, frame.f_back.f_back.f_code.co_name
        split_tag = ";;;"
        file_name = re.sub(r"[\\/]", split_tag, co_filename).split(split_tag)[-1]
        message = f"[{ time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) }] | {logging.getLevelName(level)} | [{file_name}:{f_lineno}:{f_name}] - {message}"
        return message


    def debug(self, message, *args, **kwargs):
        try:
            self._logger_dict[logging.DEBUG].debug( self._fix_stack_info(logging.DEBUG, message), *args, **kwargs )
        except:
            self._logger_dict[logging.INFO].debug( self._fix_stack_info(logging.WARNING, message), *args, **kwargs )


    def info(self, message, *args, **kwargs):
        self._logger_dict[logging.INFO].info( self._fix_stack_info(logging.INFO, message), *args, **kwargs )


    def warning(self, message, *args, **kwargs):
        try:
            self._logger_dict[logging.WARNING].warning( self._fix_stack_info(logging.WARNING, message), *args, **kwargs )
        except:
            self._logger_dict[logging.INFO].warning( self._fix_stack_info(logging.WARNING, message), *args, **kwargs )


    def error(self, message, *args, **kwargs):
        try:
            self._logger_dict[logging.ERROR].error( self._fix_stack_info(logging.ERROR, message), *args, **kwargs )
        except:
            self._logger_dict[logging.INFO].error( self._fix_stack_info(logging.ERROR, message), *args, **kwargs )


    def exception(self, message, *args, **kwargs):
        try:
            self._logger_dict[logging.ERROR].exception( self._fix_stack_info(logging.ERROR, message), *args, **kwargs )
        except:
            self._logger_dict[logging.INFO].exception( self._fix_stack_info(logging.ERROR, message), *args, **kwargs )


    def critical(self, message, *args, **kwargs):
        try:
            self._logger_dict[logging.CRITICAL].critical( self._fix_stack_info(logging.CRITICAL, message), *args, **kwargs )
        except:
            self._logger_dict[logging.INFO].critical( self._fix_stack_info(logging.CRITICAL, message), *args, **kwargs )


    def log(self, level, msg, *args, **kwargs):
        level_func = self.log_dict[level]
        level_func(msg, *args, **kwargs)
        
 

my_logger = MyLogging(level=logging._nameToLevel.get(LOG_LEVEL) )

if __name__ == '__main__':
    print(log_root_dir)