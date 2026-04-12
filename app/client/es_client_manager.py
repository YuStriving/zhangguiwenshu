"""Elasticsearch客户端管理器模块

此模块负责管理Elasticsearch的客户端连接，提供初始化和关闭连接的功能。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typing import Optional
from elasticsearch import AsyncElasticsearch
from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    """Elasticsearch客户端管理器类
    
    负责管理Elasticsearch的客户端连接，提供初始化和关闭连接的方法。
    """
    
    def __init__(self, config: ESConfig):
        """初始化Elasticsearch客户端管理器
        
        参数:
            config: ESConfig - Elasticsearch配置对象
        """
        self.client: Optional[AsyncElasticsearch] = None
        self.config: ESConfig = config

    def _get_url(self) -> str:
        """获取Elasticsearch服务的URL
        
        返回:
            str - Elasticsearch服务的URL
        """
        return f"http://{self.config.host}:{self.config.port}"
    
    async def init(self):
        """初始化Elasticsearch客户端连接
        
        创建并初始化AsyncElasticsearch实例，连接到配置的Elasticsearch服务。
        """
        self.client = AsyncElasticsearch(
            hosts=[self._get_url()]
        )
    
    async def close(self):
        """关闭Elasticsearch客户端连接
        
        关闭当前的AsyncElasticsearch连接。
        """
        if self.client:
            await self.client.close()


# 创建Elasticsearch客户端管理器实例
# 使用应用配置中的Elasticsearch配置
es_client_manager = ESClientManager(app_config.es)


async def test():
    """测试函数，用于测试Elasticsearch客户端
    
    测试初始化客户端、创建索引、添加文档、查询文档等操作。
    """
    print("初始化Elasticsearch客户端...")
    await es_client_manager.init()
    print("Elasticsearch客户端初始化成功")
    
    try:
        # 测试数据
        index_name = app_config.es.index_name
        
        # 检查索引是否存在，如果不存在则创建
        index_exists = await es_client_manager.client.indices.exists(index=index_name)
        
        if not index_exists.body:
            print(f"创建索引: {index_name}")
            await es_client_manager.client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "id": {
                                "type": "keyword"
                            },
                            "title": {
                                "type": "text",
                                "analyzer": "ik_max_word",
                                "search_analyzer": "ik_smart"
                            },
                            "content": {
                                "type": "text",
                                "analyzer": "ik_max_word",
                                "search_analyzer": "ik_smart"
                            },
                            "category": {
                                "type": "keyword"
                            },
                            "created_at": {
                                "type": "date"
                            }
                        }
                    }
                }
            )
            print(f"索引 {index_name} 创建成功")
        else:
            print(f"索引 {index_name} 已存在")
        
        # 准备测试文档
        print("准备测试文档...")
        documents = [
            {
                "id": "1",
                "title": "测试文档1",
                "content": "这是第一个测试文档，用于测试Elasticsearch功能",
                "category": "test",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": "2",
                "title": "测试文档2",
                "content": "这是第二个测试文档，用于测试Elasticsearch搜索",
                "category": "test",
                "created_at": "2024-01-02T00:00:00"
            }
        ]
        
        # 添加测试文档
        print("添加测试文档...")
        for doc in documents:
            await es_client_manager.client.index(
                index=index_name,
                id=doc["id"],
                body=doc
            )
        print("测试文档添加成功")
        
        # 刷新索引
        await es_client_manager.client.indices.refresh(index=index_name)
        
        # 测试搜索
        print("测试搜索...")
        search_results = await es_client_manager.client.search(
            index=index_name,
            body={
                "query": {
                    "match": {
                        "content": "测试"
                    }
                }
            }
        )
        
        print("搜索结果:")
        for hit in search_results["hits"]["hits"]:
            print(f"ID: {hit['_id']}, 标题: {hit['_source']['title']}")
        
        # 获取索引信息
        print("获取索引信息...")
        index_info = await es_client_manager.client.indices.get(index=index_name)
        print(f"索引信息: {index_info}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 关闭客户端
        print("关闭Elasticsearch客户端...")
        await es_client_manager.close()
        print("Elasticsearch客户端关闭成功")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
