from dataclasses import dataclass
from typing import Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.meta_column import MetaColumn


@dataclass
class ColumnInfo:
    """列信息实体类
    
    用于在不同层之间传递列信息数据，与SQLAlchemy ORM模型解耦。
    """
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    role: Optional[str] = None
    examples: Optional[List[Any]] = None
    description: Optional[str] = None
    alias: Optional[List[str]] = None
    table_id: Optional[str] = None
    
    @classmethod
    def from_orm(cls, meta_column: 'MetaColumn') -> 'ColumnInfo':
        """从ORM模型转换为实体类
        
        Args:
            meta_column: SQLAlchemy ORM模型实例
            
        Returns:
            ColumnInfo: 转换后的实体类实例
        """
        return cls(
            id=meta_column.id,
            name=meta_column.name,
            type=meta_column.type,
            role=meta_column.role,
            examples=meta_column.examples,
            description=meta_column.description,
            alias=meta_column.alias,
            table_id=meta_column.table_id
        )
    
    def to_orm(self) -> 'MetaColumn':
        """转换为ORM模型
        
        Returns:
            MetaColumn: 转换后的ORM模型实例
        """
        from app.models.meta_column import MetaColumn
        return MetaColumn(
            id=self.id,
            name=self.name,
            type=self.type,
            role=self.role,
            examples=self.examples,
            description=self.description,
            alias=self.alias,
            table_id=self.table_id
        )
    
    def __repr__(self):
        return f"ColumnInfo(id='{self.id}', name='{self.name}', type='{self.type}', role='{self.role}')"