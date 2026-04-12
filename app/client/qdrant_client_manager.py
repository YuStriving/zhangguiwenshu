"""Qdrant客户端管理器模块

此模块负责管理Qdrant向量数据库的客户端连接，提供初始化和关闭连接的功能。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typing import Optional
from qdrant_client import AsyncQdrantClient
from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    """Qdrant客户端管理器类
    
    负责管理Qdrant向量数据库的客户端连接，提供初始化和关闭连接的方法。
    """
    
    def __init__(self, config: QdrantConfig):
        """初始化Qdrant客户端管理器
        
        参数:
            config: QdrantConfig - Qdrant配置对象
        """
        self.client: Optional[AsyncQdrantClient] = None
        self.config: QdrantConfig = config

    def _get_url(self) -> str:
        """获取Qdrant服务的URL
        
        返回:
            str - Qdrant服务的URL
        """
        return f"http://{self.config.host}:{self.config.port}"
    
    async def init(self):
        """初始化Qdrant客户端连接
        
        创建并初始化AsyncQdrantClient实例，连接到配置的Qdrant服务。
        """
        self.client = AsyncQdrantClient(
            url=self._get_url()
        )
    
    async def close(self):
        """关闭Qdrant客户端连接
        
        关闭当前的AsyncQdrantClient连接。
        """
        if self.client:
            await self.client.close()


# 创建Qdrant客户端管理器实例
# 使用应用配置中的Qdrant配置
qdrant_client_manager = QdrantClientManager(app_config.qdrant)


async def test():
    """主函数，用于测试Qdrant客户端
    
    测试初始化客户端、创建集合、添加向量数据、查询向量等操作。
    """
    import numpy as np
    
    print("初始化Qdrant客户端...")
    await qdrant_client_manager.init()
    print("Qdrant客户端初始化成功")
    
    try:
        # 测试数据
        collection_name = "test_collection"
        
        # 检查集合是否存在，如果不存在则创建
        collections = await qdrant_client_manager.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name not in collection_names:
            print(f"创建集合: {collection_name}")
            from qdrant_client.http.models import VectorParams
            await qdrant_client_manager.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=app_config.qdrant.embedding_size,
                    distance="Cosine"
                )
            )
            print(f"集合 {collection_name} 创建成功")
        else:
            print(f"集合 {collection_name} 已存在")
        
        # 生成测试向量数据
        print("生成测试向量数据...")
        vectors = np.random.rand(5, app_config.qdrant.embedding_size).tolist()
        payloads = [
            {"id": i, "name": f"item_{i}", "category": "test"}
            for i in range(5)
        ]
        
        # 添加向量数据
        print("添加向量数据...")
        await qdrant_client_manager.client.upsert(
            collection_name=collection_name,
            points=[
                {
                    "id": i,
                    "vector": vectors[i],
                    "payload": payloads[i]
                }
                for i in range(5)
            ]
        )
        print("向量数据添加成功")
        
        # 获取集合信息
        print("获取集合信息...")
        collection_info = await qdrant_client_manager.client.get_collection(collection_name=collection_name)
        print(f"集合信息: {collection_info}")
        
        # 测试获取点
        print("测试获取点...")
        points = await qdrant_client_manager.client.retrieve(
            collection_name=collection_name,
            ids=[0, 1, 2]
        )
        print("获取的点:")
        for point in points:
            print(f"ID={point.id}, 数据={point.payload}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 关闭客户端
        print("关闭Qdrant客户端...")
        await qdrant_client_manager.close()
        print("Qdrant客户端关闭成功")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())

