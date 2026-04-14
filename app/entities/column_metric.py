from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.meta_column_metric import MetaColumnMetric


@dataclass
class ColumnMetric:
    """列指标关联实体类
    
    用于在不同层之间传递列指标关联数据，与SQLAlchemy ORM模型解耦。
    """
    column_id: str
    metric_id: str
    
    @classmethod
    def from_orm(cls, meta_column_metric: 'MetaColumnMetric') -> 'ColumnMetric':
        """从ORM模型转换为实体类
        
        Args:
            meta_column_metric: SQLAlchemy ORM模型实例
            
        Returns:
            ColumnMetric: 转换后的实体类实例
        """
        return cls(
            column_id=meta_column_metric.column_id,
            metric_id=meta_column_metric.metric_id
        )
    
    def to_orm(self) -> 'MetaColumnMetric':
        """转换为ORM模型
        
        Returns:
            MetaColumnMetric: 转换后的ORM模型实例
        """
        from app.models.meta_column_metric import MetaColumnMetric
        return MetaColumnMetric(
            column_id=self.column_id,
            metric_id=self.metric_id
        )
    
    def __repr__(self):
        return f"ColumnMetric(column_id='{self.column_id}', metric_id='{self.metric_id}')"