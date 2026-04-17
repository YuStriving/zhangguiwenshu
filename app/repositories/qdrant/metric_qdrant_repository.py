from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qdrant_client.async_qdrant_client import AsyncQdrantClient

# 导入必要的类型
from app.entities.metric_info import MetricInfo

class MetricQdrantRepository:
    """指标Qdrant仓库类
    
    用于与Qdrant数据库进行指标相关的CRUD操作。
    
    功能说明:
        - 指标信息的向量化存储和检索
        - 集合管理和维度验证
        - 相似度搜索和阈值过滤
        
    参数说明:
        qdrant_client: AsyncQdrantClient - Qdrant异步客户端实例
        
    使用场景:
        - 数据智能体指标信息召回
        - 元数据知识库构建
        - 相似指标搜索和推荐
    """
    
    def __init__(self, qdrant_client: 'AsyncQdrantClient') -> None:
        """初始化指标Qdrant仓库
        
        Args:
            qdrant_client: Qdrant异步客户端实例
        """
        self.qdrant_client = qdrant_client
        self.collection_name = "metric_info_collection"
        
    async def ensure_collection_exists(self, collection_name: str) -> None:
        """确保指标集合存在
        
        检查集合是否存在，如果不存在则创建，如果维度不匹配则重新创建。
        
        Args:
            collection_name: 指标集合名称
            
        Raises:
            Exception: 集合操作失败时抛出异常
            
        Logs:
            - 集合存在状态
            - 集合创建操作
        """
        from app.core.log import logger
        
        try:
            # 检查集合是否存在
            collection_info = await self.qdrant_client.get_collection(collection_name)
            logger.info(
                "指标集合已存在",
                extra={
                    "method": "ensure_collection_exists",
                    "collection_name": collection_name,
                    "dimension": collection_info.config.params.vectors.size
                }
            )
            
        except Exception:
            # 集合不存在，创建新集合
            logger.info(
                "创建新指标集合",
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
                collection_name="metric_info_collection",
                points=points
            )
    async def search(self, embedding: list, score_threshold: float = 0.5, limit: int = 10) -> list:
        """搜索相似的指标
        
        Args:
            embedding: 查询向量
            score_threshold: 最小相似度阈值
            limit: 最大返回数量
        
        Returns:
            相似的指标列表
        """
        # 搜索相似的指标
        # 执行Qdrant搜索
        results = await self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        metric_infos =  [MetricInfo(**point.payload) for point in results.points]
        return metric_infos
