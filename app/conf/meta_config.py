"""元数据配置模块

此模块定义了元数据配置的结构，包括表、列和指标的定义。
使用OmegaConf库来加载和管理配置，支持从YAML文件中读取配置。
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from omegaconf import OmegaConf

@dataclass
class ColumnConfig:
    """列配置类

    属性:
        name: str - 列的名称
        role: str - 列的角色 (e.g., primary_key, dimension, measure, foreign_key)
        description: str - 列的描述
        alias: List[str] - 列的别名列表
        sync: bool - 是否同步该列
    """
    name: str
    role: str
    description: str
    alias: List[str]
    sync: bool

@dataclass
class TableConfig:
    """表配置类

    属性:
        name: str - 表的名称
        role: str - 表的角色 (e.g., dim, fact)
        description: str - 表的描述
        columns: List[ColumnConfig] - 表中的列配置列表
    """
    name: str
    role: str
    description: str
    columns: List[ColumnConfig]

@dataclass
class MetricConfig:
    """指标配置类

    属性:
        name: str - 指标的名称
        description: str - 指标的描述
        relevant_columns: List[str] - 相关列的列表
        alias: List[str] - 指标的别名列表
    """
    name: str
    description: str
    relevant_columns: List[str]
    alias: List[str]

@dataclass
class MetaConfig:
    """元数据主配置类

    属性:
        tables: List[TableConfig] - 表配置列表
        metrics: List[MetricConfig] - 指标配置列表
    """
    tables: List[TableConfig]
    metrics: List[MetricConfig]

# 配置文件路径
config_path = Path(__file__).parents[2] / 'conf' / 'meta_config.yaml'

# 加载配置文件
conf = OmegaConf.load(config_path)

# 创建配置 schema
schema = OmegaConf.structured(MetaConfig)

# 合并配置并转换为对象
meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, conf))

# 示例：打印第一个表的名称和第一个指标的名称
# print(meta_config.tables[0].name)
# print(meta_config.metrics[0].name)
