# 自动导包配置
from app.core.path_config import PROJECT_ROOT
import sys
import os

# 确保项目根目录在路径中
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.conf.app_config import app_config
from langchain_openai import ChatOpenAI

# 阿里云模型配置 - 添加超时和重试机制
llm = ChatOpenAI(
    model=app_config.llm.model_name,
    openai_api_base=app_config.llm.base_url,
    openai_api_key=app_config.llm.api_key,
    temperature=0,
    timeout=30,  # 30秒超时
    max_retries=3  # 最大重试次数
)

if __name__ == "__main__":
    try:
        response = llm.invoke("你好")
        # 处理Windows终端的编码问题
        content = response.content
        # 移除所有非ASCII字符
        import re
        content = re.sub(r'[^\x00-\x7F\u4e00-\u9FFF]', '', content)
        print(content)
    except Exception as e:
        print(f"错误: {e}")
    
