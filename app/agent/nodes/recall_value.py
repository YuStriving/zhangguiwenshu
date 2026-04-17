import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# 导入必要的类型
from app.entities.value_info import ValueInfo
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write({"type":"progress","step":"值召回","status":"running"})
    
    try:
        query = state['query']
        keywords = state['keywords']
        value_es_repository = runtime.context['value_es_repository']
        prompt = PromptTemplate(
            template = load_prompt("extend_keywords_for_value_recall"),
            input_variables = ["query"],
        )
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({"query": query})
        keywords = set(result + keywords)
        value_info_map:dict[str,ValueInfo] = {}
        # 根据关键词召回字段取值
        for keyword in keywords:
            current_values_infos: list[ValueInfo] = await value_es_repository.search(keyword)
            for value_info in current_values_infos:
                if value_info.id  not in value_info_map:
                    value_info_map[value_info.id] = value_info
        retrieved_value_info:list[ValueInfo] = list(value_info_map.values())
        logger.info(f"取到的字段信息: {list(value_info_map.keys())}")
        
        write({"type":"progress","step":"值召回","status":"success"})
        return {"retrieved_value_info": retrieved_value_info}
    except Exception as e:
        logger.error(f"值召回过程中出错: {e}")
        write({"type":"progress","step":"值召回","status":"error"})
        write({"type":"error", "message": str(e)})
        raise
        



    