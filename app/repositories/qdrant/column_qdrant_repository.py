from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qdrant_client.async_qdrant_client import AsyncQdrantClient

class ColumnQdrantRepository:
    """列Qdrant存储库类
    
    用于与Qdrant数据库交互，存储和检索列信息。
    """
    def __init__(self, qdrant_client: 'AsyncQdrantClient') -> None:
        self.qdrant_client = qdrant_client
    
    async def ensure_collection_exists(self, collection_name: str) -> None:
        """确保Qdrant集合存在
        
        Args:
            collection_name: 集合名称
        """
        try:
            # 检查集合是否存在
            collection_info = await self.qdrant_client.get_collection(collection_name)
            print(f"集合 {collection_name} 已存在")
            
            # 检查集合维度是否匹配
            current_dim = collection_info.config.params.vectors.size
            expected_dim = 1024  # 实际embedding服务返回1024维向量
            
            if current_dim != expected_dim:
                print(f"集合维度不匹配: 当前{current_dim}维，期望{expected_dim}维，重新创建集合")
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
                print(f"集合 {collection_name} 重新创建完成")
                
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
                collection_name="column_info_collection",
                points=points
            )
