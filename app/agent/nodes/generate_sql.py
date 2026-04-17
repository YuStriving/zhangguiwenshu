import sys
import os

import yaml
from langchain_core.prompts import PromptTemplate

from app.agent.llm import llm
from app.core.log import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
from app.prompt.prompt_loader import load_prompt
from langchain_core.output_parsers import StrOutputParser
 
async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write({"type":"progress","step":"生成SQL","status":"running"})
    
    try:
        table_info = state['table_infos']
        query = state['query']
        date_info = state['date_info']
        metric_infos = state['metric_infos']
        db_info = state['db_info']
        prompt = PromptTemplate(
            template=load_prompt("generate_sql"),
            input_variables=['query', 'table_infos', 'date_info', 'metric_infos', 'db_info'],
        )
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({
            "query": query,
            "table_infos": yaml.dump(table_info, sort_keys=False,encoding='utf-8',allow_unicode=True),
            "date_info": yaml.dump(date_info, sort_keys=False,encoding='utf-8',allow_unicode=True),
            "metric_infos": yaml.dump(metric_infos, sort_keys=False,encoding='utf-8',allow_unicode=True),
            "db_info": yaml.dump(db_info, sort_keys=False,encoding='utf-8',allow_unicode=True)
        })
        logger.info(f"生成的SQL: {result}")
        
        write({"type":"progress","step":"生成SQL","status":"success"})
        return {"sql": result}
    except Exception as e:
        logger.error(f"生成SQL过程中出错: {e}")
        write({"type":"progress","step":"生成SQL","status":"error"})
        write({"type":"error", "message": str(e)})
        raise