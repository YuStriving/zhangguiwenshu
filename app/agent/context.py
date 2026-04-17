from typing import TypedDict

# 导入必要的类型
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.client.embedding_client_manager import EmbeddingClientManager
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository

class DataAgentContext(TypedDict):
    """数据智能体上下文类"""
    column_qdrant_repository: ColumnQdrantRepository
    embedding_client_manager: EmbeddingClientManager
    metric_qdrant_repository: MetricQdrantRepository
    value_es_repository: ValueESRepository
    meta_mysql_repository: MetaMySQLRepository
    
 