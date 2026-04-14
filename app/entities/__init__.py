"""实体类模块

此模块包含与数据库表对应的数据实体类，用于在不同层之间传递数据。
这些实体类与SQLAlchemy ORM模型解耦，便于单元测试和业务逻辑处理。
"""

from .table_info import TableInfo
from .column_info import ColumnInfo
from .metric_info import MetricInfo
from .column_metric import ColumnMetric

__all__ = [
    'TableInfo',
    'ColumnInfo', 
    'MetricInfo',
    'ColumnMetric'
]