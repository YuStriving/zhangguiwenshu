from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qdrant_client.async_qdrant_client import AsyncQdrantClient

# 导入必要的类型
from app.entities.column_info import ColumnInfo

class ColumnQdrantRepository:
    """列Qdrant存储库类
    
    用于与Qdrant数据库交互，存储和检索列信息。
    
    功能说明:
        - 列信息的向量化存储和检索
        - 集合管理和维度验证
        - 相似度搜索和阈值过滤
        
    参数说明:
        qdrant_client: AsyncQdrantClient - Qdrant异步客户端实例
        collection_name: str - 集合名称，默认为"column_info_collection"
        
    使用场景:
        - 数据智能体字段信息召回
        - 元数据知识库构建
        - 相似字段搜索和推荐
    """
    def __init__(self, qdrant_client: 'AsyncQdrantClient') -> None:
        """初始化列Qdrant存储库
        
        Args:
            qdrant_client: Qdrant异步客户端实例
        """
        self.qdrant_client = qdrant_client
        self.collection_name = "column_info_collection"
    
    async def ensure_collection_exists(self, collection_name: str) -> None:
        """确保Qdrant集合存在
        
        检查集合是否存在，如果不存在则创建，如果维度不匹配则重新创建。
        
        Args:
            collection_name: 集合名称
            
        Raises:
            Exception: 集合操作失败时抛出异常
            
        Logs:
            - 集合存在状态
            - 维度匹配检查结果
            - 集合创建/删除操作
        """
        from app.core.log import logger
        
        try:
            # 检查集合是否存在
            collection_info = await self.qdrant_client.get_collection(collection_name)
            logger.info(
                "集合已存在",
                extra={
                    "method": "ensure_collection_exists",
                    "collection_name": collection_name,
                    "dimension": collection_info.config.params.vectors.size
                }
            )
            
            # 检查集合维度是否匹配
            current_dim = collection_info.config.params.vectors.size
            expected_dim = 1024  # 实际embedding服务返回1024维向量
            
            if current_dim != expected_dim:
                logger.warning(
                    "集合维度不匹配，重新创建集合",
                    extra={
                        "method": "ensure_collection_exists",
                        "collection_name": collection_name,
                        "current_dimension": current_dim,
                        "expected_dimension": expected_dim
                    }
                )
                # 删除现有集合
                await self.qdrant_client.delete_collection(collection_name)
                # 创建新集合
                await self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "size": expected_dim,
                        "distance": "Cosine"  # 使用余弦相似度
                    }
                )
                logger.info(
                    "集合重新创建完成",
                    extra={
                        "method": "ensure_collection_exists",
                        "collection_name": collection_name,
                        "dimension": expected_dim
                    }
                )
                
        except Exception:
            # 集合不存在，创建新集合
            logger.info(
                "创建新集合",
                extra={
                    "method": "ensure_collection_exists",
                    "collection_name": collection_name,
                    "dimension": 1024
                }
            )
            await self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "size": 1024,  # 实际embedding服务返回1024维向量
                    "distance": "Cosine"  # 使用余弦相似度
                }
            )
    
    async def upsert(self, ids: list, embeddings: list, payloads: list) -> None:
        """批量插入或更新向量数据到Qdrant
        
        Args:
            ids: 向量ID列表
            embeddings: 向量数据列表
            payloads: 元数据列表
        """
        # 构建Qdrant点数据
        points = []
        for i, (vector_id, embedding, payload) in enumerate(zip(ids, embeddings, payloads)):
             point = {
                "id": vector_id,
                "vector": embedding,
                "payload": payload
            }
             points.append(point)
        
        # 批量插入到Qdrant
        if points:
            await self.qdrant_client.upsert(
                collection_name="column_info_collection",
                points=points
            )
    async def search(self, embedding: list[float], score_threshold: float = 0.5, limit: int = 10) -> list[ColumnInfo]:
        """搜索相似的列
        
        Args:
            embedding: 查询向量
            score_threshold: 最小相似度阈值
            limit: 最大返回结果数
        
        Returns:
            相似列列表
        """
        # 执行Qdrant搜索
        results = await self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        column_infos =  [ColumnInfo(**point.payload) for point in results.points]
        return column_infos

