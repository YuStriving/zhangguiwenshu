"""日志管理模块

此模块负责配置和管理应用程序的日志系统，支持文件日志和控制台日志。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
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
    
    def _setup_logger(self):
        """设置日志配置
        
        根据配置设置文件日志和控制台日志。
        """
        # 清除默认的logger配置
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
    
    def get_logger(self):
        """获取配置好的logger实例
        
        返回:
            logger - 配置好的logger实例
        """
        return logger


# 创建日志管理器实例
# 使用应用配置中的日志配置
log_manager = LogManager(app_config.logging)

# 导出logger实例，方便其他模块直接使用
logger = log_manager.get_logger()


if __name__ == "__main__":
    """测试日志功能"""
    # 测试不同级别的日志
    logger.debug("这是一个debug级别的日志")
    logger.info("这是一个info级别的日志")
    logger.warning("这是一个warning级别的日志")
    logger.error("这是一个error级别的日志")
    logger.critical("这是一个critical级别的日志")
    
    # 测试异常日志
    try:
        1 / 0
    except Exception as e:
        logger.exception("发生异常:")
