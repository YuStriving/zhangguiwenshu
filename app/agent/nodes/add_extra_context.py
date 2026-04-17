import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from datetime import date
from app.agent.state import DBInfoState, DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
from app.agent.state import DateInfoState
from app.core.log import logger
async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
   write = runtime.stream_writer
   write("开始添加额外上下文")
   dw_mysql_repository = runtime.context.get('dw_mysql_repository')  # 数据仓库仓库不存在
   today = date.today()
   date_str = today.strftime("%Y-%m-%d")
   weekday_str = today.strftime("%A")
   quarter_str = f"Q{(today.month - 1)  // 3 + 1}"
   date_info  = DateInfoState(date=date_str, weekday=weekday_str, quarter=quarter_str) 
   db = await dw_mysql_repository.get_db_info()
   db_info = DBInfoState(**db)
   logger.info(f"数据库信息: {db_info}")
   logger.info(f"日期信息: {date_info}")
   return {'date_info': date_info, 'db_info': db_info}

   pass
