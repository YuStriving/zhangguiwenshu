import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
import yaml
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

async def filter_metric_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write("开始指标信息过滤")
    metric_infos = state['metric_infos']
    query = state['query']
    prompt = PromptTemplate(
        template = load_prompt("filter_metric_info"),
        input_variables = ["query", "metric_infos"],
    )
    output_parser = JsonOutputParser()
    chain = prompt | llm | output_parser
    result = await chain.ainvoke({"query": query, "metric_infos": yaml.dump(metric_infos,encoding="utf-8",allow_unicode=True,sort_keys=False)})
    filtered_metric_infos:list[MetricInfoState] = []
    for metric_info in metric_infos:
        if metric_info['name'] in result:
            filtered_metric_infos.append(metric_info)
    logger.info(f"过滤后的指标信息数量: {len(filtered_metric_infos)}")
    return {"metric_infos": filtered_metric_infos}
    pass