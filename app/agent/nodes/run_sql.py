import sys
import os

from app.core.log import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime

async def run_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write({"type":"progress","step":"执行SQL语句","status":"running"})
    
    try:
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        sql = state["sql"]
        result = await dw_mysql_repository.run_sql(sql)
        logger.info(f"sql语句的运行结果为：{result}")
        
        write({"type":"progress","step":"执行SQL语句","status":"success"})
        write({"type":"result", "data": result})
        return {"result": result}
    except Exception as e:
        logger.error(f"执行SQL语句过程中出错: {e}")
        write({"type":"progress","step":"执行SQL语句","status":"error"})
        write({"type":"error", "message": str(e)})
        raise