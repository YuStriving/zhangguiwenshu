from dataclasses import asdict
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.entities.column_info import ColumnInfo
    from app.models.meta_column import MetaColumn


class ColumnInfoMapper:
    """列信息映射器类
    
    用于将列信息实体类转换为ORM模型，或从ORM模型转换为实体类。
    """
    
    @staticmethod
    def to_entity(meta_column: 'MetaColumn') -> 'ColumnInfo':
        """将ORM模型转换为实体类
        
        Args:
            meta_column: SQLAlchemy ORM模型实例
            
        Returns:
            ColumnInfo: 转换后的实体类实例
        """
        return ColumnInfo(
            id=meta_column.id,
            name=meta_column.name,
            type=meta_column.type,
            role=meta_column.role,
            examples=meta_column.examples,
            description=meta_column.description,
            alias=meta_column.alias,
            table_id=meta_column.table_id
        )
    
    @staticmethod
    def to_model(column_info: 'ColumnInfo') -> 'MetaColumn':
        """将实体类转换为ORM模型
        
        Args:
            column_info: ColumnInfo实体类实例
            
        Returns:
            MetaColumn: 转换后的ORM模型实例
        """
        from app.models.meta_column import MetaColumn
        return MetaColumn(**asdict(column_info))
    
    @staticmethod
    def to_entity_list(meta_columns: List['MetaColumn']) -> List['ColumnInfo']:
        """批量转换ORM模型列表为实体类列表
        
        Args:
            meta_columns: ORM模型列表
            
        Returns:
            List[ColumnInfo]: 实体类列表
        """
        return [ColumnInfoMapper.to_entity(column) for column in meta_columns]
    
    @staticmethod
    def to_model_list(column_infos: List['ColumnInfo']) -> List['MetaColumn']:
        """批量转换实体类列表为ORM模型列表
        
        Args:
            column_infos: 实体类列表
            
        Returns:
            List[MetaColumn]: ORM模型列表
        """
        return [ColumnInfoMapper.to_model(info) for info in column_infos]