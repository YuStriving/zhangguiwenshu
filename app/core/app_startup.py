"""应用启动模块

负责应用启动时的依赖注入容器初始化和服务注册。
"""
import asyncio
from app.core.di import Container
from app.core.service_registry import ServiceRegistry


class AppStartup:
    """应用启动器"""
    
    def __init__(self):
        self.container = Container()
    
    async def startup(self) -> Container:
        """启动应用，初始化所有服务
        
        Returns:
            Container: 初始化完成的依赖注入容器
        """
        # 注册所有服务
        ServiceRegistry.register_services(self.container)
        
        # 预初始化关键服务（确保依赖关系正确）
        await self._pre_initialize_services()
        
        return self.container
    
    async def _pre_initialize_services(self):
        """预初始化关键服务"""
        # 这里可以添加需要预初始化的服务
        # 例如：确保数据库连接正常等
        pass
    
    async def shutdown(self):
        """关闭应用，清理资源"""
        self.container.clear()


# 全局应用启动器实例
_app_startup = AppStartup()


async def get_container() -> Container:
    """获取全局依赖注入容器
    
    Returns:
        Container: 依赖注入容器实例
    """
    return await _app_startup.startup()


async def startup_event():
    """FastAPI 启动事件处理函数"""
    await get_container()


async def shutdown_event():
    """FastAPI 关闭事件处理函数"""
    await _app_startup.shutdown()