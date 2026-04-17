"""依赖注入容器模块

提供依赖注入容器功能，用于解耦服务之间的依赖关系。
"""
import asyncio
from typing import Dict, Any, Type, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum


class ServiceLifetime(Enum):
    """服务生命周期"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"


@dataclass
class ServiceRegistration:
    """服务注册信息"""
    service_type: Type
    implementation: Union[Type, Callable]
    lifetime: ServiceLifetime
    instance: Optional[Any] = None


class Container:
    """依赖注入容器
    
    用于管理服务依赖关系，实现依赖注入模式。
    """
    
    def __init__(self):
        """初始化容器"""
        self._registrations: Dict[Type, ServiceRegistration] = {}
    
    def register_singleton(self, service_type: Type, implementation: Union[Type, Callable]) -> None:
        """注册单例服务
        
        Args:
            service_type: 服务类型
            implementation: 服务实现类或工厂函数
        """
        self._registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON
        )
    
    def register_transient(self, service_type: Type, implementation: Union[Type, Callable]) -> None:
        """注册瞬态服务
        
        Args:
            service_type: 服务类型
            implementation: 服务实现类或工厂函数
        """
        self._registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT
        )
    
    def get(self, service_type: Type) -> Optional[Any]:
        """获取服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例，如果未注册则返回None
        """
        if service_type not in self._registrations:
            return None
        
        registration = self._registrations[service_type]
        
        # 如果是单例且已有实例，直接返回
        if registration.lifetime == ServiceLifetime.SINGLETON and registration.instance is not None:
            return registration.instance
        
        # 创建实例
        implementation = registration.implementation
        if isinstance(implementation, type):
            # 如果是类，自动解析依赖并实例化
            instance = self._create_instance(implementation)
        else:
            # 如果是工厂函数，调用函数
            instance = implementation(self)
            # 如果工厂函数返回协程，等待它完成
            if asyncio.iscoroutine(instance):
                instance = asyncio.run(instance)
        
        # 如果是单例，保存实例
        if registration.lifetime == ServiceLifetime.SINGLETON:
            registration.instance = instance
        
        return instance
    
    def _create_instance(self, cls: Type) -> Any:
        """自动创建实例并解析依赖
        
        Args:
            cls: 要实例化的类
            
        Returns:
            实例化后的对象
        """
        # 获取构造函数的参数注解
        import inspect
        signature = inspect.signature(cls.__init__)
        parameters = {}
        
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            # 获取参数类型注解
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                raise ValueError(f"参数 {param_name} 缺少类型注解")
            
            # 从容器中获取依赖
            dependency = self.get(param_type)
            if dependency is None:
                raise ValueError(f"无法解析依赖: {param_type}")
            
            parameters[param_name] = dependency
        
        return cls(**parameters)
    
    def has(self, service_type: Type) -> bool:
        """检查服务是否已注册
        
        Args:
            service_type: 服务类型
            
        Returns:
            如果服务已注册返回True，否则返回False
        """
        return service_type in self._registrations
    
    def unregister(self, service_type: Type) -> None:
        """注销服务
        
        Args:
            service_type: 服务类型
        """
        if service_type in self._registrations:
            del self._registrations[service_type]
    
    def clear(self) -> None:
        """清空所有注册的服务"""
        self._registrations.clear()