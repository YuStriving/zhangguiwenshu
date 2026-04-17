"""日志管理模块

此模块负责配置和管理应用程序的日志系统，支持文件日志和控制台日志。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from loguru import logger
from app.conf.app_config import LoggingConfig, app_config


class LogManager:
    """日志管理器类
    
    负责配置和管理应用程序的日志系统。
    """
    
    def __init__(self, config: LoggingConfig):
        """初始化日志管理器
        
        参数:
            config: LoggingConfig - 日志配置对象
        """
        self.config: LoggingConfig = config
        self._setup_logger()
    
    def get_calling_module(self) -> str:
        """获取调用日志的模块名称
        
        返回:
            str - 模块名称 (如 'agent', 'service', 'repository' 等)
        """
        import inspect
        
        frame = inspect.currentframe()
        
        # 第一次遍历：优先寻找 app.开头的模块
        temp_frame = frame
        while temp_frame:
            module_name = temp_frame.f_globals.get('__name__', 'unknown')
            
            # 跳过日志模块本身
            if not module_name.startswith('app.core.log'):
                # 优先处理 app.开头的模块
                if module_name.startswith('app.'):
                    parts = module_name.split('.')
                    if len(parts) >= 3:
                        # 支持多级路径，但只返回第一级子模块名
                        # app.agent.nodes → agent
                        # app.repositories.mysql.meta → repositories
                        if parts[1] in ['agent', 'service', 'repository', 'repositories', 'client']:
                            return parts[1]
                    elif len(parts) == 2:
                        return parts[1]
            
            temp_frame = temp_frame.f_back
        
        # 第二次遍历：如果没找到 app.开头的模块，尝试从__main__的文件路径提取
        temp_frame = frame
        while temp_frame:
            module_name = temp_frame.f_globals.get('__name__', 'unknown')
            
            if module_name == '__main__':
                # 获取调用栈的文件路径
                filename = temp_frame.f_code.co_filename
                if filename and 'app' in filename:
                    # 从文件路径中提取模块信息
                    app_index = filename.find('app')
                    if app_index != -1:
                        # 提取 app 后面的路径部分
                        relative_path = filename[app_index:].replace('\\', '/').replace('.py', '')
                        path_parts = relative_path.split('/')
                        if len(path_parts) >= 3:
                            # app/agent/nodes → agent
                            # app/repositories/mysql/dw → repositories
                            if path_parts[1] in ['agent', 'service', 'repository', 'repositories', 'client']:
                                return path_parts[1]
                            else:
                                return path_parts[1]
                        elif len(path_parts) == 2:
                            return path_parts[1]
            
            temp_frame = temp_frame.f_back
        
        return 'unknown'
    
    def get_program_log_path(self, program_name: str) -> Path:
        """获取程序模块日志路径
        
        参数:
            program_name: str - 程序模块名称
            
        返回:
            Path - 程序模块日志目录路径
        """
        base_path = Path(self.config.program_logging.base_path)
        # 直接使用服务类型作为文件夹名，不需要添加 logs.前缀
        program_path = base_path / program_name
        program_path.mkdir(exist_ok=True, parents=True)
        return program_path
    
    def _setup_logger(self):
        """设置日志配置
        
        根据配置设置文件日志和控制台日志。
        """
        # 清除默认的 logger 配置
        logger.remove()
        
        # 配置文件日志
        if self.config.file.enable:
            # 确保日志目录存在
            log_path = Path(self.config.file.path)
            log_path.mkdir(exist_ok=True, parents=True)
            
            # 添加文件处理器
            logger.add(
                str(log_path / "app.log"),
                level=self.config.file.level,
                rotation=self.config.file.rotation,
                retention=self.config.file.retention,
                encoding="utf-8",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
                backtrace=True,
                diagnose=True
            )
        
        # 配置控制台日志
        if self.config.console.enable:
            # 添加控制台处理器
            logger.add(
                sys.stdout,
                level=self.config.console.level,
                colorize=True,
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                backtrace=True,
                diagnose=True
            )
        
        # 配置程序模块日志
        if self.config.program_logging.enable:
            self._setup_program_logger()
    
    def _setup_program_logger(self):
        """设置程序模块日志处理器
        
        为不同的程序模块创建独立的日志文件，按日期轮转
        """
        # 为每个核心服务类型创建独立的日志处理器
        service_types = ['agent', 'service', 'repository', 'repositories', 'client']
        
        for service_type in service_types:
            # 获取程序模块日志路径
            program_path = self.get_program_log_path(service_type)
            
            # 创建过滤器，只记录对应服务的日志
            def filter_func(record, service=service_type):
                # 从记录中获取模块名
                module_name = record['name']
                if module_name.startswith('app.'):
                    parts = module_name.split('.')
                    if len(parts) >= 2:
                        return parts[1] == service
                return False
            
            # 添加程序模块文件处理器（按日期轮转）
            logger.add(
                str(program_path / "{time:YYYY-MM-DD}.log"),  # 动态日期文件名
                level=self.config.program_logging.level,
                rotation=self.config.program_logging.rotation,
                retention=self.config.program_logging.retention,
                encoding="utf-8",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
                backtrace=True,
                diagnose=True,
                filter=filter_func
            )
    
    def get_logger(self):
        """获取配置好的 logger 实例
        
        返回:
            logger - 配置好的 logger 实例
        """
        return logger


# 创建日志管理器实例
# 使用应用配置中的日志配置
log_manager = LogManager(app_config.logging)

# 导出 logger 实例，方便其他模块直接使用
logger = log_manager.get_logger()


if __name__ == "__main__":
    """测试日志功能"""
    # 测试不同级别的日志
    logger.debug("这是一个 debug 级别的日志")
    logger.info("这是一个 info 级别的日志")
    logger.warning("这是一个 warning 级别的日志")
    logger.error("这是一个 error 级别的日志")
    logger.critical("这是一个 critical 级别的日志")
    
    # 测试异常日志
    try:
        1 / 0
    except Exception as e:
        logger.exception("发生异常:")
