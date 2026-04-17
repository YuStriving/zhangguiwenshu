import sys
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.llm import llm
from app.entities import ColumnInfo
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime

async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    """
    列信息召回节点 - 基于关键词从向量数据库中召回相关列信息
    
    功能说明:
    - 使用LLM扩展关键词，增强召回效果
    - 对每个关键词进行向量化
    - 从Qdrant向量数据库中搜索匹配的列信息
    - 去重处理，避免重复列信息
    
    参数:
        state: DataAgentState - 数据智能体状态
        runtime: Runtime[DataAgentContext] - 运行时上下文
        
    返回:
        DataAgentState - 更新后的状态，包含召回的列信息列表
    """
    write = runtime.stream_writer
    write({"type":"progress","step":"列信息召回","status":"running"})
    
    try:
        # 获取状态和上下文信息
        keywords = state['keywords']
        query = state['query']
        column_qdrant_repository = runtime.context['column_qdrant_repository']
        embedding_client = runtime.context['embedding_client_manager']
        
        # 构建LLM提示词链
        prompt = PromptTemplate(
            template = load_prompt("extend_keywords_for_column_recall"),
            input_variables = ["query"],
        )
        output_parser = JsonOutputParser()
        
        # 借助LLM扩展关键词
        logger.debug(
            "开始LLM关键词扩展",
            extra={
                "method": "recall_column",
                "original_keywords_count": len(keywords),
                "query": query
            }
        )
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({"query": query})
        
        # 合并原始关键词和扩展后的关键词
        keywords = set(result + keywords)
        logger.debug(
            "关键词扩展完成",
            extra={
                "method": "recall_column",
                "extended_keywords_count": len(keywords),
                "new_keywords_added": len(result)
            }
        )
        
        # 用于存储去重后的列信息
        column_info_map:dict[str, ColumnInfo] = {}
        
        # 对每个关键词进行向量化搜索
        logger.debug(
            "开始向量化搜索",
            extra={
                "method": "recall_column",
                "total_keywords": len(keywords),
                "score_threshold": 0.6,
                "limit_per_keyword": 10
            }
        )
        
        for keyword in keywords:
            # 对keyword进行向量化
            embeddings = await embedding_client.get_embeddings([keyword])
            embedding = embeddings[0]
            
            # 从向量数据库中搜索匹配的列信息
            current_column_infos: list[ColumnInfo] = await column_qdrant_repository.search(
                embedding, 
                score_threshold=0.6,  # 相似度阈值
                limit=10  # 最大返回数量
            )
            
            # 去重处理，避免重复列信息
            for column_info in current_column_infos:
                if column_info.id not in column_info_map:
                    column_info_map[column_info.id] = column_info
        
        # 处理完成后返回结果
        retrieved_column_info:list[ColumnInfo] = list(column_info_map.values())
        
        # 记录召回结果
        logger.info(
            "列信息召回完成",
            extra={
                "method": "recall_column",
                "query": query,
                "keywords_count": len(keywords),
                "retrieved_columns_count": len(retrieved_column_info),
                "retrieved_columns": list(column_info_map.keys())
            }
        )
        
        write({"type":"progress","step":"列信息召回","status":"success"})
        logger.info(f"列信息召回完成，共召回{len(retrieved_column_info)}个字段")
        return {"retrieved_column_info": retrieved_column_info}
    except Exception as e:
        logger.error(f"列信息召回过程中出错: {e}")
        write({"type":"progress","step":"列信息召回","status":"error"})
        write({"type":"error", "message": str(e)})
        raise