import uuid

from aiohttp.web_request import Request
from fastapi import FastAPI
from langsmith import middleware

from app.api.routers.query_router import query_router

app = FastAPI()
app.include_router(query_router)
@middleware("http")
async def add_process_time_handler(request:Request, call_next):
    # 请求处理之前
    request_id = uuid.uuid4()   
    request_id_context_var.set(request_id)
    response = await call_next(request)
    # 请求处理之后
    return response
