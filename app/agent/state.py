
from calendar import weekday
from typing import TypedDict

# 导入必要的类型
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo


class MetricInfoState(TypedDict):
    name:str
    description:str
    alias:list
    relevant_columns:list[str]
    
class ColumnInfoState(TypedDict):
    name:str
    role:str
    description:str
    type:str
    examples:list
    alias:list


class TableInfoState(TypedDict):
    name:str
    role:str
    description:str
    columns:list[ColumnInfoState]

class DateInfoState(TypedDict):
    date : str
    weekday: str
    quarter: str


class DBInfoState(TypedDict):
    version: str  
    dialect: str


class DataAgentState(TypedDict):
    """数据智能体状态类"""
    query: str # 用户输入的查询语句
    error: str # 校验sql时出现的错误信息
    keywords: list[str] # 取到的关词
    retrieved_column_info: list[ColumnInfo] # 取到的列信息
    retrieved_value_info: list[ValueInfo] # 取到的字段取值信息
    retrieved_metric_info: list[MetricInfo] # 取到的指标信息
    table_infos:list[TableInfoState]
    metric_infos:list[MetricInfoState]
    date_info:DateInfoState # 日期信息
    db_info:DBInfoState # 数据库信息
    sql:str # 生成的SQL语句