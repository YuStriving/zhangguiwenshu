from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.client.embedding_client_manager import EmbeddingClientManager
from app.client.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class QueryService:
    """查询服务
    
    负责处理自然语言查询，生成 SQL 并返回结果。
    """
    
    def __init__(
        self,
        meta_repository: MetaMySQLRepository,
        dw_repository: DWMySQLRepository,
        column_repository: ColumnQdrantRepository,
        metric_repository: MetricQdrantRepository,
        value_repository: ValueESRepository,
        embedding_manager: EmbeddingClientManager
    ):
        """初始化查询服务
        
        Args:
            meta_repository: 元数据仓储
            dw_repository: 数据仓库仓储
            column_repository: 列向量仓储
            metric_repository: 指标向量仓储
            value_repository: 值仓储
            embedding_manager: 嵌入向量管理器
        """
        self.meta_repository = meta_repository
        self.dw_repository = dw_repository
        self.column_repository = column_repository
        self.metric_repository = metric_repository
        self.value_repository = value_repository
        self.embedding_manager = embedding_manager
    
    async def query(self, query: str):
        """执行查询语句，返回结果
        
        Args:
            query: 自然语言查询语句
            
        Yields:
            查询结果的流式输出
        """
        state = DataAgentState(query=query)
        context = DataAgentContext(
            column_qdrant_repository=self.column_repository,
            embedding_client_manager=self.embedding_manager,
            metric_qdrant_repository=self.metric_repository,
            value_es_repository=self.value_repository,
            meta_mysql_repository=self.meta_repository,
            dw_mysql_repository=self.dw_repository
        )
        
        async for chunk in graph.astream(
            input=state, 
            context=context, 
            stream_mode="custom"
        ):
            yield f"data: {chunk}\n\n"
        await qdrant_client_manager.close()