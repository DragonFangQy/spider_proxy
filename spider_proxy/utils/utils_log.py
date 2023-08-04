
import os
import logging
import inspect
import re

import colorlog

from logging.handlers import TimedRotatingFileHandler



base_file_path = os.path.dirname( os.path.dirname(__file__) )
# LOG_PATH 
LOG_PATH = os.getenv("LOG_PATH", base_file_path+"/logs/")
LOG_ONLY_CONSOLE = os.getenv("LOG_ONLY_CONSOLE", "False")
print(LOG_PATH)

# level info 20 debug 10
log_level = os.getenv("LOG_LEVEL", logging.INFO)
# 默认debug 只log debug
log_info_not_look_debug = os.getenv("LOG_INFO_NOT_LOOK_DEBUG", "False")
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

# 控制日志输出路径，
# 必须包含 logging.INFO
LOG_INFO = {
    logging.DEBUG: {
            "log_file_path": LOG_PATH+"/debug/service.log",
            "log_formatter": LOG_FORMATTER,
        },
    logging.INFO: {
            "log_file_path": LOG_PATH+"/info/service.log",
            "log_formatter": LOG_FORMATTER,
        },
    logging.ERROR: {
            "log_file_path": LOG_PATH+"/error/service.log",
            "log_formatter": LOG_FORMATTER,
        },
}

class Logger(logging.Logger):
    def __init__(self, name, level='DEBUG', encoding='utf-8', print_console=True):
        super().__init__(name)
        
        self.print_console = print_console
        self.encoding = encoding
        self.level = level
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(self.level)
        self.__logger.propagate = False

        self.EXCEPTION = 45
        
        # 创建日志目录
        self._make_log_folder()

    @staticmethod
    def _make_log_folder():
        LOG_INFO.get(logging.INFO)

        # 创建日志目录
        for log_info in LOG_INFO.values():
            log_file_path = log_info.get("log_file_path")

            save_dir = "/".join(log_file_path.split("/")[:-1])
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
    
    def __add_log_handler(self, level, handler_list):

        # 首先添加 info
        log_info = LOG_INFO.get(level)
        log_file_path = log_info.get("log_file_path")
        log_handler = TimedRotatingFileHandler(
                            filename=log_file_path, 
                            when="MIDNIGHT", 
                            interval=1,
                            backupCount=30,
                            encoding="utf-8"
                            )
        
        log_formatter = log_info.get("log_formatter")

        if not isinstance(log_handler, logging.Handler):
            raise ValueError(f"{log_handler} not isinstance logging.Handler ")

        log_handler.setFormatter(log_formatter) 
        log_handler.setLevel(level)
        handler_list.append(log_handler)
        self.__logger.addHandler(log_handler)

    def _set_log_handler(self, level):
        
        handler_list = []

        if LOG_ONLY_CONSOLE.lower() == "False".lower():
            # 首先添加 info
            self.__add_log_handler(logging.INFO, handler_list)

            for log_level, log_info in LOG_INFO.items():

                # 特殊处理，将 EXCEPTION 的等级调整为 ERROR
                # 以便添加 Handler
                if level == self.EXCEPTION:
                    level = logging.ERROR

                # 特殊处理，只添加对应 level 的Handler
                # 以便每个 level 都可以有自己的 file
                # 但同时跳过 logging.INFO，
                # 因为每个等级必须包含 这个 Handler
                # 以便于在 info 中看到所有的 log
                if level != log_level or level == logging.INFO:
                    continue

                # 添加对应 level 的 handler
                self.__add_log_handler(logging.INFO, handler_list)

            # 默认info 中看不见 debug
            if level == logging.DEBUG and log_info_not_look_debug.lower() != "True".lower() :
                handler_list = handler_list[1:]

        # 最后添加 控制台输出
        if self.print_console:
            console_handler = colorlog.StreamHandler()

            log_formatter = LOG_INFO.get(logging.INFO).get("log_formatter")
            console_handler.setFormatter(log_formatter) 
            console_handler.setLevel(level=logging.INFO)

            handler_list.append(console_handler)
            self.__logger.addHandler(console_handler)

        return handler_list

    def _close_handler(self, handler_list):

        for log_handler in handler_list:
            self.__logger.removeHandler(log_handler)
            if not isinstance(log_handler, logging.Handler):
                raise ValueError(f"{log_handler} not isinstance logging.Handler ")
            log_handler.close()
            
        handler_list = []


    def debug(self, message):
        self.__console(logging.DEBUG, message)

    def info(self, message):
        self.__console(logging.INFO, message)

    def warning(self, message):
        self.__console(logging.WARNING, message)

    def error(self, message):
        self.__console(logging.ERROR, message)

    def exception(self, message):
        self.__console(self.EXCEPTION, message)

    def critical(self, message):
        self.__console(logging.CRITICAL, message)

    def __console(self, level, message):
            
            # 
            handler_list = self._set_log_handler(level)
            self.__logger.info(f"__console handler_list start :{len(handler_list)}")


            level_dict = {
                logging.DEBUG:self.__logger.debug,
                logging.INFO:self.__logger.info,
                logging.WARNING:self.__logger.warning,
                logging.ERROR:self.__logger.error,
                self.EXCEPTION:self.__logger.exception,
                logging.CRITICAL:self.__logger.critical,
            }

            # inspect
            frame = inspect.currentframe()
            co_filename, f_lineno, f_name = frame.f_back.f_back.f_code.co_filename, frame.f_back.f_back.f_lineno, frame.f_back.f_back.f_code.co_name
            co_filename = re.sub(r"\\", "/", co_filename)
            co_filename = co_filename.split("/")[-1]

            message = message+'\n'
            _message = f"[{co_filename}:{f_lineno}:{f_name}] - {message}"

            log_func = level_dict.get(level) 
            log_func(_message) 

            self._close_handler(handler_list)
            self.__logger.info(f"__console handler_list end:{len(handler_list)}")


log_name = "log_name.log"

my_logger = Logger(name=log_name, level=int(log_level))
