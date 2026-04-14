from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.meta_table import MetaTable


@dataclass
class TableInfo:
    """表信息实体类
    
    用于在不同层之间传递表信息数据，与SQLAlchemy ORM模型解耦。
    """
    id: str
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    
    @classmethod
    def from_orm(cls, meta_table: 'MetaTable') -> 'TableInfo':
        """从ORM模型转换为实体类
        
        Args:
            meta_table: SQLAlchemy ORM模型实例
            
        Returns:
            TableInfo: 转换后的实体类实例
        """
        return cls(
            id=meta_table.id,
            name=meta_table.name,
            role=meta_table.role,
            description=meta_table.description
        )
    
    def to_orm(self) -> 'MetaTable':
        """转换为ORM模型
        
        Returns:
            MetaTable: 转换后的ORM模型实例
        """
        from app.models.meta_table import MetaTable
        return MetaTable(
            id=self.id,
            name=self.name,
            role=self.role,
            description=self.description
        )
    
    def __repr__(self):
        return f"TableInfo(id='{self.id}', name='{self.name}', role='{self.role}')"