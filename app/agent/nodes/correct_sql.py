import sys
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.llm import llm
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime

async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write({"type":"progress","step":"修正SQL语句","status":"running"})
    
    try:
        table_info  = state["table_infos"]
        metric_info = state["metric_infos"]
        date_info = state["date_info"]
        db_info = state["db_info"]
        sql = state["sql"]
        error = state["error"]
        query = state["query"]

        prompt = PromptTemplate(
            template = load_prompt("correct_sql"),
            input_variables = ["sql", "query", "table_info", 
            "metric_info", "date_info", "db_info", "error"]
        )
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({"sql":sql, "query":query, "table_infos":table_info, 
        "metric_infos":metric_info, "date_info":date_info, "db_info":db_info, "error":error})
        logger.info(f"修正后的SQL: {result}")
        
        write({"type":"progress","step":"修正SQL语句","status":"success"})
        return {"sql":result}
    except Exception as e:
        logger.error(f"修正SQL语句过程中出错: {e}")
        write({"type":"progress","step":"修正SQL语句","status":"error"})
        write({"type":"error", "message": str(e)})
        raise