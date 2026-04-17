"""服务注册模块

统一管理所有服务的注册和依赖关系。
"""
import asyncio
from app.core.di import Container
from app.conf.app_config import app_config, EmbeddingConfig
from app.client.embedding_client_manager import EmbeddingClientManager, embedding_client_manager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.client.es_client_manager import es_client_manager
from app.client.mysql_client_manager import mysql_meta_client_manager, mysql_dw_client_manager
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.service.query_service import QueryService


class ServiceRegistry:
    """服务注册器"""
    
    @classmethod
    async def register_services(cls, container: Container) -> None:
        """注册所有服务到容器中
        
        Args:
            container: 依赖注入容器
        """
        # 注册配置类（单例）
        container.register_singleton(EmbeddingConfig, lambda c: app_config.embedding)
        
        # 初始化全局客户端管理器
        await embedding_client_manager.init()
        
        # 注册客户端管理器（单例）- 使用全局实例以兼容 Agent 层
        container.register_singleton(EmbeddingClientManager, lambda c: embedding_client_manager)
        
        # 预初始化所有仓储服务
        meta_repository = await cls._create_meta_repository(container)
        dw_repository = await cls._create_dw_repository(container)
        column_repository = await cls._create_column_repository(container)
        metric_repository = await cls._create_metric_repository(container)
        value_repository = await cls._create_value_repository(container)
        
        # 注册仓储服务（单例）- 使用预初始化的实例
        container.register_singleton(MetaMySQLRepository, lambda c: meta_repository)
        container.register_singleton(DWMySQLRepository, lambda c: dw_repository)
        container.register_singleton(ColumnQdrantRepository, lambda c: column_repository)
        container.register_singleton(MetricQdrantRepository, lambda c: metric_repository)
        container.register_singleton(ValueESRepository, lambda c: value_repository)
        
        # 注册业务服务（瞬态）
        container.register_transient(QueryService, QueryService)
    
    @staticmethod
    async def _create_meta_repository(container: Container) -> MetaMySQLRepository:
        """创建元数据仓储实例"""
        await mysql_meta_client_manager.init()
        session = await mysql_meta_client_manager.get_session().__anext__()
        return MetaMySQLRepository(session)
    
    @staticmethod
    async def _create_dw_repository(container: Container) -> DWMySQLRepository:
        """创建数据仓库仓储实例"""
        await mysql_dw_client_manager.init()
        session = await mysql_dw_client_manager.get_session().__anext__()
        return DWMySQLRepository(session)
    
    @staticmethod
    async def _create_column_repository(container: Container) -> ColumnQdrantRepository:
        """创建列向量仓储实例"""
        await qdrant_client_manager.init()
        return ColumnQdrantRepository(qdrant_client_manager.client)
    
    @staticmethod
    async def _create_metric_repository(container: Container) -> MetricQdrantRepository:
        """创建指标向量仓储实例"""
        await qdrant_client_manager.init()
        return MetricQdrantRepository(qdrant_client_manager.client)
    
    @staticmethod
    async def _create_value_repository(container: Container) -> ValueESRepository:
        """创建值仓储实例"""
        await es_client_manager.init()
        return ValueESRepository(es_client_manager.client)