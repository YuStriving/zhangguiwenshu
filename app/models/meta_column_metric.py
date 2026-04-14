from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.meta_data import Base

class MetaColumnMetric(Base):
    """列与指标关联模型

    存储列与指标的关联关系，对应数据库中的 `column_metric` 表。
    这是一个关联表，用于表示 MetaColumn 和 MetaMetric 之间的多对多关系。
    """
    __tablename__ = 'column_metric'

    column_id = Column(String(64), ForeignKey('column_info.id'), primary_key=True, comment='列编号')
    metric_id = Column(String(64), ForeignKey('metric_info.id'), primary_key=True, comment='指标编号')

    # 定义与 MetaColumn 和 MetaMetric 的关系，方便通过关联表访问
    # 注意：这里不需要 back_populates，因为在 MetaColumn 和 MetaMetric 中已经定义了 secondary 关系
    # 但是可以添加 relationship 来直接访问关联对象
    # 添加 overlaps 参数来明确关系边界，避免 SQLAlchemy 警告
    column = relationship('MetaColumn', overlaps="columns,metrics")
    metric = relationship('MetaMetric', overlaps="columns,metrics")

    def __repr__(self):
        return f"<MetaColumnMetric(column_id='{self.column_id}', metric_id='{self.metric_id}')>"
