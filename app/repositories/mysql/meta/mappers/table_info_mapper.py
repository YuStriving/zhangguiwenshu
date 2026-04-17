from dataclasses import asdict
from typing import TYPE_CHECKING
from app.entities.table_info import TableInfo

if TYPE_CHECKING:
    from app.models.meta_table import MetaTable


class TableInfoMapper:
    """表信息映射器类
    用于将表信息实体类转换为ORM模型，或从ORM模型转换为实体类。
    """
    
    @staticmethod
    def to_entity(meta_table: 'MetaTable') -> 'TableInfo':
        """将ORM模型转换为实体类
        
        Args:
            meta_table: SQLAlchemy ORM模型实例
            
        Returns:
            TableInfo: 转换后的实体类实例
        """
        return TableInfo(
            id=meta_table.id,
            name=meta_table.name,
            role=meta_table.role,
            description=meta_table.description
        )
    
    @staticmethod
    def to_model(table_info: 'TableInfo') -> 'MetaTable':
        """转换为ORM模型
        
        Returns:
            MetaTable: 转换后的ORM模型实例
        """
        from app.models.meta_table import MetaTable
        return MetaTable(**asdict(table_info))
