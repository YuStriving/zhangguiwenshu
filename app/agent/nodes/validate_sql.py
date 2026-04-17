import sys
import os

from app.core.log import logger
from app.repositories.mysql.dw import dw_mysql_repository

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime

async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write({"type":"progress","step":"验证SQL语句","status":"running"})
    
    try:
        sql = state["sql"]
        dw_mysql_repository = runtime.context["dw_mysql_repository"]
        try:
            await dw_mysql_repository.validate_sql(sql)
            logger.info("SQL语句验证成功")
            
            write({"type":"progress","step":"验证SQL语句","status":"success"})
            return {"error":None}
        except Exception as e:
            logger.error(e)
            
            write({"type":"progress","step":"验证SQL语句","status":"error"})
            write({"type":"error", "message": str(e)})
            return {"error":str(e)}
    except Exception as e:
        logger.error(f"验证SQL语句过程中出错: {e}")
        write({"type":"progress","step":"验证SQL语句","status":"error"})
        write({"type":"error", "message": str(e)})
        raise