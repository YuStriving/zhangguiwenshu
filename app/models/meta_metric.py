from sqlalchemy import Column, String, JSON, Text
from sqlalchemy.orm import relationship
from app.models.meta_data import Base

class MetaMetric(Base):
    """元数据指标模型

    存储数据仓库中指标的元数据信息，对应数据库中的 `metric_info` 表。
    """
    __tablename__ = 'metric_info'

    id = Column(String(64), primary_key=True, index=True, comment='指标编码')
    name = Column(String(128), nullable=True, comment='指标名称')
    description = Column(Text, nullable=True, comment='指标描述')
    relevant_columns = Column(JSON, nullable=True, comment='关联的列')
    alias = Column(JSON, nullable=True, comment='指标别名')

    # 定义与 MetaColumn 的多对多关系，通过 column_metric 表
    columns = relationship('MetaColumn', secondary='column_metric', back_populates='metrics')

    def __repr__(self):
        return f"<MetaMetric(id={self.id}, name='{self.name}')>"
