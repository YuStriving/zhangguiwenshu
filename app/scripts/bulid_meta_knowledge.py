import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.client.qdrant_client_manager import qdrant_client_manager
from app.client.mysql_client_manager import mysql_dw_client_manager, mysql_meta_client_manager
from app.client.embedding_client_manager import embedding_client_manager, EmbeddingClientManager
from app.client.es_client_manager import es_client_manager  # 添加ES客户端管理器
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.service.meta_knowledge_service import MetaKnowledgeService
from app.core.di import Container

from app.repositories.es.value_es_repository import ValueESRepository

async def build(config_path: Path):
    """
    异步构建元数据。该函数会实例化 MetaKnowledgeService 并调用其 build 方法来执行元数据构建过程。

    Args:
        config_path (Path): 包含元数据配置信息的YAML文件路径，例如表结构、列定义和指标等。
    """
    try:
        # 初始化客户端管理器（需要await）
        await mysql_meta_client_manager.init()
        await mysql_dw_client_manager.init()
        await embedding_client_manager.init()
        await qdrant_client_manager.init()
        await es_client_manager.init()
        # 直接获取Session，手动管理事务
        async with mysql_meta_client_manager.get_session() as meta_session:
            async with mysql_dw_client_manager.get_session() as dw_session:
                # 创建存储库实例
                meta_repository = MetaMySQLRepository(meta_session)
                dw_repository = DWMySQLRepository(dw_session)
                column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
                value_es_repository = ValueESRepository(es_client_manager.client)
                metric_qdrant_repository = MetricQdrantRepository(qdrant_client_manager.client)
                
               
                # 创建依赖注入容器并注册服务
                container = Container()
                container.register(MetaMySQLRepository, meta_repository)
                container.register(DWMySQLRepository, dw_repository)
                container.register(ColumnQdrantRepository, column_qdrant_repository)
                container.register(EmbeddingClientManager, embedding_client_manager) 
                container.register(ValueESRepository, value_es_repository)
                container.register(MetricQdrantRepository, metric_qdrant_repository)
                
                # 创建服务实例并执行构建
                meta_service = MetaKnowledgeService(container)
                await meta_service.build(config_path)
                
    except Exception as e:
        print(f"构建元数据时发生错误: {e}")
        raise
    finally:
        # 关闭客户端管理器（需要await）
        await mysql_meta_client_manager.close()
        await mysql_dw_client_manager.close()
        await qdrant_client_manager.close()

def main():
    """主函数"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "conf" / "meta_config.yaml"
    asyncio.run(build(config_path))

if __name__ == "__main__":
    main()