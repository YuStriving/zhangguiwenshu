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
from app.core.log import logger


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
    
    async def ensure_index_exists(self, index_name: str, mappings: Optional[dict] = None) -> None:
        """确保Elasticsearch索引存在
        
        Args:
            index_name: 索引名称
            mappings: 索引映射配置，如果为None则使用默认配置
        """
        # 检查索引是否存在
        index_exists = await self.client.indices.exists(index=index_name)
        
        if not index_exists.body:
            logger.debug(f"创建索引: {index_name}")
            
            # 使用提供的映射配置或默认配置
            if mappings is None:
                mappings = {
                    "dynamic": False,
                    "properties": {
                        "id": {"type": "keyword"},
                        "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
                        "column_id": {"type": "keyword"}
                    }
                }
            
            await self.client.indices.create(
                index=index_name,
                body={"mappings": mappings}
            )
            logger.info(f"索引 {index_name} 创建成功")
        else:
            logger.info(f"索引 {index_name} 已存在")


# 创建Elasticsearch客户端管理器实例
# 使用应用配置中的Elasticsearch配置
es_client_manager = ESClientManager(app_config.es)


async def test():
    """测试函数，用于测试Elasticsearch客户端
    
    测试初始化客户端、创建索引、添加文档、查询文档等操作。
    """
    logger.debug("初始化Elasticsearch客户端...")
    await es_client_manager.init()
    logger.info("Elasticsearch客户端初始化成功")
    
    try:
        # 测试数据
        index_name = app_config.es.index_name
        
        # 使用新方法确保索引存在
        await es_client_manager.ensure_index_exists(index_name)
        
        # 准备测试文档
        logger.debug("准备测试文档...")
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
        logger.debug("添加测试文档...")
        for doc in documents:
            await es_client_manager.client.index(
                index=index_name,
                id=doc["id"],
                body=doc
            )
        logger.info("测试文档添加成功")
        
        # 刷新索引
        await es_client_manager.client.indices.refresh(index=index_name)
        
        # 测试搜索
        logger.debug("测试搜索...")
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
        
        logger.info(f"搜索结果: {len(search_results['hits']['hits'])} 条")
        # 只在debug级别显示具体结果
        for hit in search_results["hits"]["hits"]:
            logger.debug(f"ID: {hit['_id']}, 标题: {hit['_source']['title']}")
        
        # 获取索引信息
        logger.debug("获取索引信息...")
        index_info = await es_client_manager.client.indices.get(index=index_name)
        logger.debug(f"索引信息: {index_info}")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
    finally:
        # 关闭客户端
        logger.debug("关闭Elasticsearch客户端...")
        await es_client_manager.close()
        logger.info("Elasticsearch客户端关闭成功")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
