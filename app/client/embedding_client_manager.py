"""嵌入服务客户端管理器模块

此模块负责管理嵌入服务的客户端连接，提供初始化和关闭连接的功能。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typing import Optional, List, Dict, Any
import aiohttp
from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    """嵌入服务客户端管理器类
    
    负责管理嵌入服务的客户端连接，提供初始化和关闭连接的方法。
    """
    
    def __init__(self, config: EmbeddingConfig):
        """初始化嵌入服务客户端管理器
        
        参数:
            config: EmbeddingConfig - 嵌入服务配置对象
        """
        self.session: Optional[aiohttp.ClientSession] = None
        self.config: EmbeddingConfig = config

    def _get_url(self) -> str:
        """获取嵌入服务的URL
        
        返回:
            str - 嵌入服务的URL
        """
        return f"http://{self.config.host}:{self.config.port}"
    
    async def init(self):
        """初始化嵌入服务客户端连接
        
        创建并初始化aiohttp.ClientSession实例，用于与Text Embedding Inference服务通信。
        """
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """关闭嵌入服务客户端连接
        
        关闭当前的aiohttp.ClientSession连接。
        """
        if self.session:
            await self.session.close()
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本的嵌入向量
        
        参数:
            texts: List[str] - 要获取嵌入向量的文本列表
            
        返回:
            List[List[float]] - 文本的嵌入向量列表
        """
        if not self.session:
            raise RuntimeError("客户端未初始化")
        
        # Text Embedding Inference服务的API端点
        url = f"{self._get_url()}/embed"
        data = {
            "inputs": texts,
            "model": self.config.model
        }
        
        async with self.session.post(url, json=data) as response:
            if response.status == 200:
                result = await response.json()
                # 直接返回嵌入向量列表
                return result
            else:
                raise Exception(f"获取嵌入向量失败: {await response.text()}")


# 创建嵌入服务客户端管理器实例
# 使用应用配置中的嵌入服务配置
embedding_client_manager = EmbeddingClientManager(app_config.embedding)


async def test():
    """测试函数，用于测试嵌入服务客户端
    
    测试初始化客户端、获取嵌入向量等操作。
    """
    print("初始化嵌入服务客户端...")
    await embedding_client_manager.init()
    print("嵌入服务客户端初始化成功")
    
    try:
        # 测试数据
        test_texts = [
            "这是第一个测试文本",
            "这是第二个测试文本",
            "这是第三个测试文本"
        ]
        
        # 获取嵌入向量
        print("获取嵌入向量...")
        embeddings = await embedding_client_manager.get_embeddings(test_texts)
        print(f"获取到嵌入向量数量: {len(embeddings)}")
        
        # 打印嵌入向量信息
        for i, embedding in enumerate(embeddings):
            print(f"文本 {i+1} 的嵌入向量维度: {len(embedding)}")
            print(f"嵌入向量前5个值: {embedding[:5]}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 关闭客户端
        print("关闭嵌入服务客户端...")
        await embedding_client_manager.close()
        print("嵌入服务客户端关闭成功")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())