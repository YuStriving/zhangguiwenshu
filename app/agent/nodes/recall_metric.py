import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# 导入必要的类型
from app.entities.metric_info import MetricInfo
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    write = runtime.stream_writer
    write({"type":"progress","step":"指标信息召回","status":"running"})
    
    try:
        query = state['query']
        keywords = state['keywords']
        embedding_client = runtime.context['embedding_client_manager']
        metric_qdrant_repository = runtime.context['metric_qdrant_repository']
        prompt = PromptTemplate(
            template = load_prompt("extend_keywords_for_metric_recall"),
            input_variables = ["query"],
        )
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        result = chain.invoke({"query": query})
        keywords = set(result + keywords)
        
        # 用于存储去重后的指标信息
        metric_info_map:dict[str, MetricInfo] = {}
        
        # 对每个关键词进行向量化搜索
        for keyword in keywords:
            # 对keyword进行向量化
            embeddings = await embedding_client.get_embeddings([keyword])
            embedding = embeddings[0]
            
            # 从向量数据库中搜索匹配的指标信息
            current_metric_infos: list[MetricInfo] = await metric_qdrant_repository.search(
                embedding, 
                score_threshold=0.6,  # 相似度阈值
                limit=10  # 最大返回数量
            )
            
            # 去重处理，避免重复指标信息
            for metric_info in current_metric_infos:
                if metric_info.id not in metric_info_map:
                    metric_info_map[metric_info.id] = metric_info
        
        # 处理完成后返回结果
        retrieved_metric_info:list[MetricInfo] = list(metric_info_map.values())
        
        # 记录召回结果
        logger.info(
            "指标信息召回完成",
            extra={
                "method": "recall_metric",
                "query": query,
                "keywords_count": len(keywords),
                "retrieved_metrics_count": len(retrieved_metric_info),
                "retrieved_metrics": list(metric_info_map.keys())
            }
        ) 
        
        write({"type":"progress","step":"指标信息召回","status":"success"})
        return {"retrieved_metric_info": retrieved_metric_info}
    except Exception as e:
        logger.error(f"指标信息召回过程中出错: {e}")
        write({"type":"progress","step":"指标信息召回","status":"error"})
        write({"type":"error", "message": str(e)})
        raise