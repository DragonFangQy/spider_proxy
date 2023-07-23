
import os
import logging
import inspect

import colorlog


from logging.handlers import TimedRotatingFileHandler
# from spider_proxy.utils.demo import TimedRotatingFileHandlerSafe as TimedRotatingFileHandler


base_file_path = os.path.dirname( os.path.dirname(__file__) )
# LOG_PATH 
LOG_PATH = os.getenv("LOG_PATH", base_file_path+"/logs/")
print(LOG_PATH)

# level info 20 debug 10
log_level = os.getenv("LOG_LEVEL", logging.INFO)
# 默认debug 只log debug
log_debug_log_all = os.getenv("LOG_DEBUG_LOG_ALL", "False")
### 日志 ###
# 定义不同日志等级颜色
log_colors_config = {
   'DEBUG': 'bold_cyan',
   'INFO': 'bold_green',
   'WARNING': 'bold_yellow',
   'ERROR': 'bold_red',
   'CRITICAL': 'red',
}

LOG_FORMATTER = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)1.1s %(asctime)s %(reset)s | '
            '%(message_log_color)s%(levelname)-8s %(reset)s| '
            '%(white)s%(message)s',
            reset=True,
            log_colors=log_colors_config,
            secondary_log_colors={
                    'message': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'bold_red'
                    }
            },
            style='%'
        ) 

# 控制日志输出路径，
# 必须包含 logging.INFO
LOG_INFO = {
    logging.DEBUG: {
            "log_file_path": LOG_PATH+"/debug/service.log",
            # "log_handler": TimedRotatingFileHandler(
            #                     filename=LOG_PATH+"/debug/service.log", 
            #                     when="MIDNIGHT", 
            #                     interval=1,
            #                     backupCount=30
            #                     ),
            "log_formatter": LOG_FORMATTER,
        },
    logging.INFO: {
            "log_file_path": LOG_PATH+"/info/service.log",
            # "log_handler": TimedRotatingFileHandler(
            #                     filename=LOG_PATH+"/info/service.log", 
            #                     when="MIDNIGHT", 
            #                     interval=1,
            #                     backupCount=30
            #                     ),
            "log_formatter": LOG_FORMATTER,
        },
    logging.ERROR: {
            "log_file_path": LOG_PATH+"/error/service.log",
            # "log_handler": TimedRotatingFileHandler(
            #                     filename=LOG_PATH+"/error/service.log", 
            #                     when="MIDNIGHT", 
            #                     interval=1,
            #                     backupCount=30
            #                     ),
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
    
    def _set_log_handler(self, level):
        
        handler_list = []
        for log_level, log_info in LOG_INFO.items():

            if level == self.EXCEPTION:
                level = logging.ERROR

            if level != log_level:
                continue

            log_file_path = log_info.get("log_file_path")
            log_handler = TimedRotatingFileHandler(
                                filename=log_file_path, 
                                when="MIDNIGHT", 
                                interval=1,
                                backupCount=30
                                )
            
            log_formatter = log_info.get("log_formatter")

            if not isinstance(log_handler, logging.Handler):
                raise ValueError(f"{log_handler} not isinstance logging.Handler ")

            log_handler.setFormatter(log_formatter) 
            log_handler.setLevel(level=log_level)
            handler_list.append(log_handler)
            self.__logger.addHandler(log_handler)
        
            # or (level != logging.DEBUG, logging.INFO) \
            # or level > logging.INFO:

        if len(handler_list) == 0 or level > logging.INFO or log_debug_log_all.lower() == "True".lower():
            # 必须存在 info
            log_info = LOG_INFO.get(logging.INFO)
            log_file_path = log_info.get("log_file_path")
            log_handler = TimedRotatingFileHandler(
                                filename=log_file_path, 
                                when="MIDNIGHT", 
                                interval=1,
                                backupCount=30
                                )
            
            log_formatter = log_info.get("log_formatter")

            if not isinstance(log_handler, logging.Handler):
                raise ValueError(f"{log_handler} not isinstance logging.Handler ")

            log_handler.setFormatter(log_formatter) 
            log_handler.setLevel(level=logging.INFO)
            handler_list.append(log_handler)
            self.__logger.addHandler(log_handler)
        elif level == logging.DEBUG:
            pass

        if self.print_console:
            console_handler = colorlog.StreamHandler()

            log_formatter = LOG_INFO.get(logging.INFO).get("log_formatter")
            console_handler.setFormatter(log_formatter) 
            console_handler.setLevel(level=logging.INFO)

            handler_list.append(console_handler)
            self.__logger.addHandler(console_handler)

        return handler_list

    def _close_handler(self, handler_list):

        # for log_info in LOG_INFO.values():
            # log_handler = log_info.get("log_handler") 

            # if not isinstance(log_handler, logging.Handler):
            #     raise ValueError(f"{log_handler} not isinstance logging.Handler ")
        for log_handler in handler_list:
            self.__logger.removeHandler(log_handler)
            if not isinstance(log_handler, logging.Handler):
                raise ValueError(f"{log_handler} not isinstance logging.Handler ")
            log_handler.close() 
        print()

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
            message = message+'\n'
            _message = f"[{co_filename}:{f_lineno}:{f_name}] - {message}"

            log_func = level_dict.get(level) 
            log_func(_message) 

            self._close_handler(handler_list)


log_name = "log_name.log"

my_logger = Logger(name=log_name, level=int(10))
