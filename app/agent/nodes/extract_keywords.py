import sys
import os
import jieba

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
from app.core.log import logger
import jieba.posseg as pseg
async def extract_keywords(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    """
    关键词提取节点 - 从用户查询中提取关键词
    
    功能说明:
    - 使用jieba分词器提取查询中的关键词
    - 根据词性过滤保留有效关键词
    - 将原始查询也作为关键词加入结果
    
    参数:
        state: DataAgentState - 数据智能体状态
        runtime: Runtime[DataAgentContext] - 运行时上下文
        
    返回:
        DataAgentState - 更新后的状态，包含提取的关键词列表
    """
    write = runtime.stream_writer
    write({"type":"progress","step":"提取关键词","status":"running"})

    query = state["query"]
    try:
        # 允许的词性列表 - 用于过滤有效关键词
        allow_pos = (
            "n",   # 名词: 数据、服务器、表格
            "nr",  # 人名: 张三、李四
            "ns",  # 地名: 北京、上海
            "nt",  # 机构团体名: 政府、学校、某公司
            "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
            "v",   # 动词: 运行、开发
            "vn",  # 名动词: 工作、研究
            "a",   # 形容词: 美丽、快速
            "an",  # 名形词: 难度、合法性、复杂度
            "eng", # 英文
            "i",   # 成语
            "l",   # 常用固定短语
        )
        
        # 使用jieba分词器提取关键词
        logger.debug(
            "开始分词处理",
            extra={
                "method": "extract_keywords",
                "query": query,
                "allowed_pos_count": len(allow_pos)
            }
        )
        words = pseg.cut(query)
        
        # 根据允许的词性过滤关键词
        kewords = [word for word, flag in words if flag in allow_pos]
        
        # 去重并添加原始查询作为关键词
        keywords = list(set(kewords + [query]))
        
        # 记录提取结果
        logger.info(
            "关键词提取完成",
            extra={
                "method": "extract_keywords",
                "query": query,
                "original_keywords_count": len(kewords),
                "final_keywords_count": len(keywords),
                "keywords": keywords
            }
        )
        
        # 返回更新后的状态
        write({"type":"progress","step":"提取关键词","status":"success"})
        return { "keywords": keywords }
    except Exception as e:
        logger.error(f"关键词提取过程中出错: {e}")
        write({"type":"progress","step":"提取关键词","status":"error"})
        write({"type":"error", "message": str(e)})
        raise 
        