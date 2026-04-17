from dataclasses import dataclass
from typing import Optional


@dataclass
class ValueInfo:
    """值信息实体类
    
    用于存储字段取值信息，支持Elasticsearch全文检索和值匹配。
    
    属性说明:
        id (str): 值信息唯一标识符
        value (str): 字段的具体取值
        column_id (str): 所属字段的ID
        
    使用场景:
        - Elasticsearch全文检索
        - 字段取值匹配和过滤
        - 数据智能体上下文构建
        
    注意事项:
        - 值信息主要用于支持模糊查询和值匹配
        - 需要与字段信息关联使用
    """
    id: str
    value: str
    column_id: str
    
