"""应用配置模块

此模块负责加载和管理应用程序的所有配置项，包括日志、数据库、向量数据库、嵌入服务、搜索引擎和语言模型等配置。
使用OmegaConf库来加载和管理配置，支持从YAML文件中读取配置。
"""

from pathlib import Path
from dataclasses import dataclass

from omegaconf import OmegaConf

# 日志配置
@dataclass
class File:
    """文件日志配置类
    
    属性:
        enable: bool - 是否启用文件日志
        level: str - 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        path: str - 日志文件路径
        rotation: str - 日志文件轮转策略
        retention: str - 日志文件保留策略
    """
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str

@dataclass
class Console:
    """控制台日志配置类
    
    属性:
        enable: bool - 是否启用控制台日志
        level: str - 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    enable: bool
    level: str

@dataclass
class LoggingConfig:
    """日志配置类
    
    属性:
        file: File - 文件日志配置
        console: Console - 控制台日志配置
    """
    file: File
    console: Console

# 数据库配置
@dataclass
class DBConfig:
    """数据库配置类
    
    属性:
        host: str - 数据库主机地址
        port: int - 数据库端口
        user: str - 数据库用户名
        password: str - 数据库密码
        database: str - 数据库名称
    """
    host: str
    port: int
    user: str
    password: str
    database: str

@dataclass
class QdrantConfig:
    """Qdrant向量数据库配置类
    
    属性:
        host: str - Qdrant主机地址
        port: int - Qdrant端口
        embedding_size: int - 嵌入向量维度
    """
    host: str
    port: int
    embedding_size: int

@dataclass
class EmbeddingConfig:
    """嵌入服务配置类
    
    属性:
        host: str - 嵌入服务主机地址
        port: int - 嵌入服务端口
        model: str - 嵌入模型名称
    """
    host: str
    port: int
    model: str

@dataclass
class ESConfig:
    """Elasticsearch配置类
    
    属性:
        host: str - Elasticsearch主机地址
        port: int - Elasticsearch端口
        index_name: str - 索引名称
    """
    host: str
    port: int
    index_name: str

@dataclass
class LLMConfig:
    """语言模型配置类
    
    属性:
        model_name: str - 模型名称
        api_key: str - API密钥
        base_url: str - API基础URL
    """
    model_name: str
    api_key: str
    base_url: str

@dataclass
class AppConfig:
    """应用主配置类
    
    属性:
        logging: LoggingConfig - 日志配置
        db_meta: DBConfig - 元数据库配置
        db_dw: DBConfig - 数据仓库配置
        qdrant: QdrantConfig - Qdrant向量数据库配置
        embedding: EmbeddingConfig - 嵌入服务配置
        es: ESConfig - Elasticsearch配置
        llm: LLMConfig - 语言模型配置
    """
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig

# 配置文件路径
# 获取当前文件的父目录的父目录的父目录，然后拼接conf/app_config.yaml
config_path = Path(__file__).parents[2] / 'conf' / 'app_config.yaml'

# 加载配置文件
conf = OmegaConf.load(config_path)

# 创建配置 schema
# 使用AppConfig类作为结构定义
schema = OmegaConf.structured(AppConfig)

# 合并配置并转换为对象
# 将加载的配置与schema合并，然后转换为AppConfig对象
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(schema, conf))

# 使用logger记录配置加载状态
from app.core.log import logger
logger.debug(f"日志配置加载成功，文件日志级别: {app_config.logging.file.level}")