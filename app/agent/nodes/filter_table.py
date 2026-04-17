from math import fabs
import sys
import os
import yaml

from app.entities import table_info

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState, TableInfoState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger
async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write("开始表信息过滤")
    query = state['query']
    table_infos = state['table_infos']
    prompt = PromptTemplate(
        template = load_prompt("filter_table_info"),
        input_variables = ["query", "table_infos"],
    )
    output_parser = JsonOutputParser()
    chain = prompt | llm | output_parser
    result = await chain.ainvoke({"query": query, "table_infos": yaml.dump(table_infos,encoding="utf-8",allow_unicode=True,sort_keys=False)})
    filtered_table_infos:list[TableInfoState] = []
    for table_info in table_infos:
        if table_info['name'] in result:
            # 保留所有主外键字段（role 为 primary 或 foreign）
            key_columns = [column_info for column_info in table_info['columns'] 
                          if column_info.get('role') in ['primary', 'foreign']]
            
            # 保留 LLM 选择的相关字段
            selected_columns = [column_info for column_info in table_info['columns'] 
                               if column_info['name'] in result[table_info['name']]]
            
            # 合并主外键字段和选中字段（去重）
            column_ids = set()
            merged_columns = []
            for col in key_columns + selected_columns:
                if col['name'] not in column_ids:
                    column_ids.add(col['name'])
                    merged_columns.append(col)
            
            table_info['columns'] = merged_columns
            filtered_table_infos.append(table_info)
    logger.info(f"过滤后的表信息数量：{len(filtered_table_infos)}")
    return {"table_infos": filtered_table_infos}
    pass