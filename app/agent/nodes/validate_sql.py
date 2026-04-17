import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime

async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    
    pass