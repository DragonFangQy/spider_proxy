
import inspect
import logging
import os
from logging.handlers import TimedRotatingFileHandler
import re
import time

# log的根目录（项目目录）
log_root_dir = os.path.dirname(os.path.dirname( os.path.dirname(__file__) ))


# 控制日志输出路径，必须包含 logging.INFO
level_log_path = {
    # logging.NOTSET: os.path.join(dir, 'D:/project/Program/ZXControl/log-%s/notset.log'%dir_time),
    logging.DEBUG: log_root_dir+"/log/debug/service.log",
    logging.INFO: log_root_dir+"/log/info/service.log",
    # logging.WARNING: os.path.join(dir, 'D:/project/Program/ZXControl/log-%s/warning.log'%dir_time),
    # logging.WARNING: log_root_dir+"/log/warn/service.log",
    logging.ERROR: log_root_dir+"/log/error/service.log",
    # logging.CRITICAL: os.path.join(dir, 'D:/project/Program/ZXControl/log-%s/critical.log'%dir_time),
}


class MyLogging(object):
    
    def __init__(self, log_name, level=logging.DEBUG, log_path=None, encoding='utf-8', backupCount=15, when='MIDNIGHT', interval=1):
        
        self._logger_dict = {}
 
        if logging.INFO not in level_log_path.keys():
            raise ValueError("level_log_path 必须包含 logging.INFO ")

        # 创建日志目录
        for log_path in level_log_path.values():

            save_dir = "/".join(log_path.split("/")[:-1])
            if os.path.exists(save_dir) is False:
                os.makedirs(save_dir)

        # 创建 loggers
        for log_level in logging._nameToLevel.values():
            
            # 控制日志输出级别, 最高优先级
            if log_level < level:
                continue
            
            log_path = level_log_path.get(log_level) 
            if level_log_path.get(log_level):
                logger = logging.Logger(log_name+f"_{log_level}")
                logger.setLevel(log_level)

                handler = self._get_handler(log_path, when=when, interval=interval, backupCount=backupCount, encoding=encoding)
                handler.setLevel(level=log_level)
                logger.addHandler(handler)
                
                self._logger_dict.update({log_level: logger})
            else:
                logger = self._logger_dict.get(logging.INFO)

                if not logger:
                    logger = logging.Logger(log_name+f"_{logging.INFO}")
                    logger.setLevel(logging.INFO)
                
                handler = self._get_handler(level_log_path.get(logging.INFO), when=when, interval=interval, backupCount=backupCount, encoding=encoding)
                handler.setLevel(level=logging.INFO)
                logger.addHandler(handler)

                self._logger_dict.update({logging.INFO: logger})
                
        print()

    def _get_handler(self, path, when='MIDNIGHT', interval=1, backupCount=30, encoding=None):
        """
        # 继承并重写可以替换 Handler
        """
        trf_handler= TimedRotatingFileHandler(path, when=when, interval=interval, backupCount=backupCount, encoding=encoding)
        return trf_handler
    
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

    def debug(self, message):

        try:
            self._logger_dict[logging.DEBUG].debug( self._fix_stack_info(logging.DEBUG, message) )
        except:
            self._logger_dict[logging.INFO].debug( self._fix_stack_info(logging.DEBUG, message) )

    def info(self, message):
        self._logger_dict[logging.INFO].info( self._fix_stack_info(logging.INFO, message) )

    def warning(self, message):
        
        try:
            self._logger_dict[logging.WARNING].warning( self._fix_stack_info(logging.WARNING, message) )
            self._logger_dict[logging.INFO].warning( self._fix_stack_info(logging.WARNING, message) )
        except:
            self._logger_dict[logging.INFO].warning( self._fix_stack_info(logging.WARNING, message) )

    def error(self, message):
        try:
            self._logger_dict[logging.ERROR].error( self._fix_stack_info(logging.ERROR, message) )
            self._logger_dict[logging.INFO].error( self._fix_stack_info(logging.ERROR, message) )
        except:
            self._logger_dict[logging.INFO].error( self._fix_stack_info(logging.ERROR, message) )

    def exception(self, message):
        
        try:
            self._logger_dict[logging.ERROR].exception( self._fix_stack_info(logging.ERROR, message) )
            self._logger_dict[logging.INFO].exception( self._fix_stack_info(logging.ERROR, message) )
        except:
            self._logger_dict[logging.INFO].exception( self._fix_stack_info(logging.ERROR, message) )

    def critical(self, message):
        
        try:
            self._logger_dict[logging.CRITICAL].critical( self._fix_stack_info(logging.CRITICAL, message) )
            self._logger_dict[logging.INFO].critical( self._fix_stack_info(logging.CRITICAL, message) )
        except:
            self._logger_dict[logging.INFO].critical( self._fix_stack_info(logging.CRITICAL, message) )


logger = MyLogging(__file__)