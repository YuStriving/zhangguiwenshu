from dataclasses import asdict
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.column_metric import ColumnMetric
    from app.models.meta_column_metric import MetaColumnMetric


class ColumnMetricMapper:
    """列指标关联映射器类
    
    用于将列指标关联实体类转换为ORM模型，或从ORM模型转换为实体类。
    """
    
    @staticmethod
    def to_entity(meta_column_metric: 'MetaColumnMetric') -> 'ColumnMetric':
        """将ORM模型转换为实体类
        
        Args:
            meta_column_metric: SQLAlchemy ORM模型实例
            
        Returns:
            ColumnMetric: 转换后的实体类实例
        """
        return ColumnMetric(
            column_id=meta_column_metric.column_id,
            metric_id=meta_column_metric.metric_id
        )
    
    @staticmethod
    def to_model(column_metric: 'ColumnMetric') -> 'MetaColumnMetric':
        """将实体类转换为ORM模型
        
        Args:
            column_metric: ColumnMetric实体类实例
            
        Returns:
            MetaColumnMetric: 转换后的ORM模型实例
        """
        from app.models.meta_column_metric import MetaColumnMetric
        return MetaColumnMetric(**asdict(column_metric))
    
    @staticmethod
    def to_entity_list(meta_column_metrics: List['MetaColumnMetric']) -> List['ColumnMetric']:
        """批量转换ORM模型列表为实体类列表
        
        Args:
            meta_column_metrics: ORM模型列表
            
        Returns:
            List[ColumnMetric]: 实体类列表
        """
        return [ColumnMetricMapper.to_entity(cm) for cm in meta_column_metrics]
    
    @staticmethod
    def to_model_list(column_metrics: List['ColumnMetric']) -> List['MetaColumnMetric']:
        """批量转换实体类列表为ORM模型列表
        
        Args:
            column_metrics: 实体类列表
            
        Returns:
            List[MetaColumnMetric]: ORM模型列表
        """
        return [ColumnMetricMapper.to_model(cm) for cm in column_metrics]