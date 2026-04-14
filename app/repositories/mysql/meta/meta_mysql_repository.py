from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.entities import ColumnInfo, TableInfo, MetricInfo, ColumnMetric
from app.models.meta_table import MetaTable
from app.models.meta_column import MetaColumn
from app.models.meta_metric import MetaMetric
from app.models.meta_column_metric import MetaColumnMetric
from app.core.log import logger
from app.repositories.mysql.meta.mappers.column_info_mapper import ColumnInfoMapper
from app.repositories.mysql.meta.mappers.table_info_mapper import TableInfoMapper
from app.repositories.mysql.meta.mappers.metric_info_mapper import MetricInfoMapper
from app.repositories.mysql.meta.mappers.column_metric_mapper import ColumnMetricMapper

class MetaMySQLRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def get_meta_table_by_id(self, table_id: str) -> Optional[MetaTable]:
        """
        根据ID获取单个MetaTable对象。
        Args:
            table_id: MetaTable的唯一标识ID。
        Returns:
            Optional[MetaTable]: 对应的MetaTable对象，如果不存在则返回None。
        """
        result = await self.session.execute(select(MetaTable).filter_by(id=table_id))
        return result.scalar_one_or_none()

    async def get_meta_column_by_id(self, column_id: str) -> Optional[MetaColumn]:
        """
        根据ID获取单个MetaColumn对象。
        Args:
            column_id: MetaColumn的唯一标识ID。
        Returns:
            Optional[MetaColumn]: 对应的MetaColumn对象，如果不存在则返回None。
        """
        result = await self.session.execute(select(MetaColumn).filter_by(id=column_id))
        return result.scalar_one_or_none()

    async def insert_meta_table(self, meta_tables: List[TableInfo]) -> None:
        """批量插入或更新MetaTable对象到数据库。"""
        try:
            # 将实体类转换为ORM模型
            models = [TableInfoMapper.to_model(meta_table) for meta_table in meta_tables]
            
            # 使用merge而不是add_all来处理插入和更新
            for model in models:
                # merge会自动检测是否存在相同主键的记录，存在则更新，不存在则插入
                merged_model = await self.session.merge(model)
                self.session.add(merged_model)
            
            # 注意：不需要commit，因为会话由外部管理
        except Exception as e:
            # 记录错误但不回滚，由外部会话管理
            raise e
           
    async def insert_meta_columns(self, meta_columns: List[ColumnInfo]) -> None:
        """批量插入或更新MetaColumn对象到数据库。"""
        try:
            # 将实体类转换为ORM模型
            models = [ColumnInfoMapper.to_model(meta_column) for meta_column in meta_columns]
            
            # 使用merge而不是add_all来处理插入和更新
            for model in models:
                # merge会自动检测是否存在相同主键的记录，存在则更新，不存在则插入
                merged_model = await self.session.merge(model)
                self.session.add(merged_model)
            
            # 注意：不需要commit，因为会话由外部管理
        except Exception as e:
            raise e
          
    async def insert_meta_metrics(self, meta_metrics: List[MetricInfo]) -> None:
        """批量插入或更新MetaMetric对象到数据库。"""
        try:
            # 将实体类转换为ORM模型
            models = [MetricInfoMapper.to_model(meta_metric) for meta_metric in meta_metrics]
            
            # 使用merge而不是add_all来处理插入和更新
            for model in models:
                # merge会自动检测是否存在相同主键的记录，存在则更新，不存在则插入
                merged_model = await self.session.merge(model)
                self.session.add(merged_model)
            
            # 注意：不需要commit，因为会话由外部管理
        except Exception as e:
            raise e

    async def insert_meta_column_metrics(self, column_metrics: List[ColumnMetric]) -> None:
        """批量插入或更新MetaColumnMetric对象到数据库。"""
        try:
            # 将实体类转换为ORM模型
            models = [ColumnMetricMapper.to_model(column_metric) for column_metric in column_metrics]
            
            # 使用merge而不是add_all来处理插入和更新
            for model in models:
                # merge会自动检测是否存在相同主键的记录，存在则更新，不存在则插入
                merged_model = await self.session.merge(model)
                self.session.add(merged_model)
            
            # 注意：不需要commit，因为会话由外部管理
        except Exception as e:
            raise e


