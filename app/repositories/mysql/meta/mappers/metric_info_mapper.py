from dataclasses import asdict
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.metric_info import MetricInfo
    from app.models.meta_metric import MetaMetric


class MetricInfoMapper:
    """指标信息映射器类
    
    用于将指标信息实体类转换为ORM模型，或从ORM模型转换为实体类。
    """
    
    @staticmethod
    def to_entity(meta_metric: 'MetaMetric') -> 'MetricInfo':
        """将ORM模型转换为实体类
        
        Args:
            meta_metric: SQLAlchemy ORM模型实例
            
        Returns:
            MetricInfo: 转换后的实体类实例
        """
        return MetricInfo(
            id=meta_metric.id,
            name=meta_metric.name,
            description=meta_metric.description,
            relevant_columns=meta_metric.relevant_columns,
            alias=meta_metric.alias
        )
    
    @staticmethod
    def to_model(metric_info: 'MetricInfo') -> 'MetaMetric':
        """将实体类转换为ORM模型
        
        Args:
            metric_info: MetricInfo实体类实例
            
        Returns:
            MetaMetric: 转换后的ORM模型实例
        """
        from app.models.meta_metric import MetaMetric
        return MetaMetric(**asdict(metric_info))
    
    @staticmethod
    def to_entity_list(meta_metrics: List['MetaMetric']) -> List['MetricInfo']:
        """批量转换ORM模型列表为实体类列表
        
        Args:
            meta_metrics: ORM模型列表
            
        Returns:
            List[MetricInfo]: 实体类列表
        """
        return [MetricInfoMapper.to_entity(metric) for metric in meta_metrics]
    
    @staticmethod
    def to_model_list(metric_infos: List['MetricInfo']) -> List['MetaMetric']:
        """批量转换实体类列表为ORM模型列表
        
        Args:
            metric_infos: 实体类列表
            
        Returns:
            List[MetaMetric]: ORM模型列表
        """
        return [MetricInfoMapper.to_model(info) for info in metric_infos]