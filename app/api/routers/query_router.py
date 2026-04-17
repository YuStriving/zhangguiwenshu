from typing import Annotated
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.api.schemas.query_schema import QuerySchema
from app.core.di import Container
from app.core.service_registry import ServiceRegistry
from app.service.query_service import QueryService


# 创建全局容器实例
_container = Container()

query_router = APIRouter()


async def get_query_service() -> QueryService:
    """获取查询服务依赖
    
    Returns:
        QueryService: 查询服务实例
    """
    # 延迟注册服务（第一次使用时注册）
    if not _container.has(QueryService):
        await ServiceRegistry.register_services(_container)
    
    query_service = _container.get(QueryService)
    if query_service is None:
        raise RuntimeError("QueryService 未在容器中注册")
    return query_service


@query_router.post("/api/query")
async def query_handler(
    query: QuerySchema,
    query_service: Annotated[QueryService, Depends(get_query_service)]
):
    """处理查询请求
    
    Args:
        query: 查询参数
        query_service: 查询服务实例
        
    Returns:
        StreamingResponse: 流式响应
    """
    return StreamingResponse(
        query_service.query(query.query),
        media_type="text/event-stream"
    )



