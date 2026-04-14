"""依赖注入容器模块

提供依赖注入容器功能，用于解耦服务之间的依赖关系。
"""
from typing import Dict, Any, Type, Optional


class Container:
    """依赖注入容器
    
    用于管理服务依赖关系，实现依赖注入模式。
    """
    
    def __init__(self):
        """初始化容器"""
        self._services: Dict[Type, Any] = {}
    
    def register(self, service_type: Type, instance: Any) -> None:
        """注册服务实例
        
        Args:
            service_type: 服务类型
            instance: 服务实例
        """
        self._services[service_type] = instance
    
    def get(self, service_type: Type) -> Optional[Any]:
        """获取服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例，如果未注册则返回None
        """
        return self._services.get(service_type)
    
    def has(self, service_type: Type) -> bool:
        """检查服务是否已注册
        
        Args:
            service_type: 服务类型
            
        Returns:
            如果服务已注册返回True，否则返回False
        """
        return service_type in self._services
    
    def unregister(self, service_type: Type) -> None:
        """注销服务
        
        Args:
            service_type: 服务类型
        """
        if service_type in self._services:
            del self._services[service_type]
    
    def clear(self) -> None:
        """清空所有注册的服务"""
        self._services.clear()