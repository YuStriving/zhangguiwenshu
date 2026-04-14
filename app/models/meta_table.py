from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.meta_data import Base

class MetaTable(Base):
    """元数据表模型

    存储数据仓库中表的元数据信息，对应数据库中的 `table_info` 表。
    """
    __tablename__ = 'table_info'

    id = Column(String(64), primary_key=True, index=True, comment='表编号')
    name = Column(String(128), nullable=True, comment='表名称')
    role = Column(String(32), nullable=True, comment='表类型(fact/dim)')
    description = Column(Text, nullable=True, comment='表描述')

    # 定义与 MetaColumn 的一对多关系
    columns = relationship('MetaColumn', back_populates='table', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<MetaTable(id={self.id}, name='{self.name}', role='{self.role}')>"
