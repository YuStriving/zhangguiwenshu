from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.meta_metric import MetaMetric


@dataclass
class MetricInfo:
    """指标信息实体类
    
    用于在不同层之间传递指标信息数据，与SQLAlchemy ORM模型解耦。
    """
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    relevant_columns: Optional[List[str]] = None
    alias: Optional[List[str]] = None
    
    @classmethod
    def from_orm(cls, meta_metric: 'MetaMetric') -> 'MetricInfo':
        """从ORM模型转换为实体类
        
        Args:
            meta_metric: SQLAlchemy ORM模型实例
            
        Returns:
            MetricInfo: 转换后的实体类实例
        """
        return cls(
            id=meta_metric.id,
            name=meta_metric.name,
            description=meta_metric.description,
            relevant_columns=meta_metric.relevant_columns,
            alias=meta_metric.alias
        )
    
    def to_orm(self) -> 'MetaMetric':
        """转换为ORM模型
        
        Returns:
            MetaMetric: 转换后的ORM模型实例
        """
        from app.models.meta_metric import MetaMetric
        return MetaMetric(
            id=self.id,
            name=self.name,
            description=self.description,
            relevant_columns=self.relevant_columns,
            alias=self.alias
        )
    
    def __repr__(self):
        return f"MetricInfo(id='{self.id}', name='{self.name}')"