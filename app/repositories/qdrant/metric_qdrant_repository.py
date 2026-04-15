from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qdrant_client.async_qdrant_client import AsyncQdrantClient

class MetricQdrantRepository:
    """指标Qdrant仓库类
    
    用于与Qdrant数据库进行指标相关的CRUD操作。
    """
    def __init__(self, qdrant_client: 'AsyncQdrantClient') -> None:
        self.qdrant_client = qdrant_client
    async def ensure_collection_exists(self, collection_name: str) -> None:
        """确保指标集合存在
        
        Args:
            collection_name: 指标集合名称
        """
        try:
            # 检查集合是否存在
            collection_info = await self.qdrant_client.get_collection(collection_name)
            print(f"集合 {collection_name} 已存在")
            
        except Exception:
            # 集合不存在，创建新集合
            print(f"创建新集合: {collection_name}")
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