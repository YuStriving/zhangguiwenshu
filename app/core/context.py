from contextvars import ContextVar
from decimal import Context


request_id_context_var:ContextVar[int] = ContextVar("request_id", default=0)