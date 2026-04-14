from sqlalchemy import Column, String, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.meta_data import Base

class MetaColumn(Base):
    """元数据列模型

    存储数据仓库中列的元数据信息，对应数据库中的 `column_info` 表。
    """
    __tablename__ = 'column_info'

    id = Column(String(64), primary_key=True, index=True, comment='列编号')
    table_id = Column(String(64), ForeignKey('table_info.id'), nullable=False, comment='所属表编号')
    name = Column(String(128), nullable=True, comment='列名称')
    type = Column(String(64), nullable=True, comment='数据类型')
    role = Column(String(32), nullable=True, comment='列角色 (primary_key,foreign_key,measure,dimension)')
    examples = Column(JSON, nullable=True, comment='数据示例')
    description = Column(Text, nullable=True, comment='列描述')
    alias = Column(JSON, nullable=True, comment='列别名')

    # 定义与 MetaTable 的多对一关系
    table = relationship('MetaTable', back_populates='columns')
    # 定义与 MetaMetric 的多对多关系，通过 column_metric 表
    metrics = relationship('MetaMetric', secondary='column_metric', back_populates='columns')

    def __repr__(self):
        return f"<MetaColumn(id={self.id}, name='{self.name}', role='{self.role}')>"
