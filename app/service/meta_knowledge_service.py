import uuid
from dataclasses import asdict
from pathlib import Path
from typing import List, Dict, Any
from app.core.log import logger

from omegaconf import OmegaConf

from app.client.embedding_client_manager import embedding_client_manager, EmbeddingClientManager
from app.conf.meta_config import MetaConfig
from app.entities import ColumnInfo, MetricInfo, TableInfo, ColumnMetric
from app.entities.value_info import ValueInfo
from app.models.meta_table import MetaTable
from app.models.meta_column import MetaColumn
from app.models.meta_metric import MetaMetric
from app.models.meta_column_metric import MetaColumnMetric
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ValueESRepository
from app.core.di import Container

class MetaKnowledgeService:

    def __init__(self, container: Container) -> None:
        """初始化元知识服务
        
        Args:
            container: 依赖注入容器，包含所有需要的仓储实例
        """
        self.container = container
        self.meta_mysql_repository: MetaMySQLRepository = container.get(MetaMySQLRepository)
        self.dw_mysql_repository: DWMySQLRepository = container.get(DWMySQLRepository)
        self.column_qdrant_repository: ColumnQdrantRepository = container.get(ColumnQdrantRepository)
        self.embedding_client_manager: EmbeddingClientManager = container.get(EmbeddingClientManager)
        self.value_es_repository: ValueESRepository = container.get(ValueESRepository)
        self.metric_qdrant_repository: MetricQdrantRepository = container.get(MetricQdrantRepository)
    async def build(self, config_path: Path) -> None:
        """
        构建元数据。该方法会读取指定的配置文件，并根据配置同步表信息和指标信息。

        Args:
            config_path (Path): 包含元数据配置信息的YAML文件路径，例如表结构、列定义和指标等。
        """
        logger.info(f"开始构建元数据知识图谱，配置文件路径: {config_path}")
        
        try:
            # 读取配置文件
            logger.debug("开始读取配置文件")
            context = OmegaConf.load(config_path)
            schema = OmegaConf.structured(MetaConfig)
            app_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
            logger.info(f"配置文件读取成功，包含 {len(app_config.tables or [])} 个表, {len(app_config.metrics or [])} 个指标")
            
            # 根据配置文件同步指定的表信息和指标信息
            if app_config.tables:
                logger.info("开始处理表元数据")
                # 处理元数据（表和列信息）
                tables, all_columns = await self._process_metadata(app_config)
                logger.info(f"元数据处理完成: {len(tables)} 个表, {len(all_columns)} 个列")
                
                # 批量插入或更新所有MetaTable和MetaColumn对象
                logger.debug("开始插入表元数据到MySQL")
                await self.meta_mysql_repository.insert_meta_table(tables)
                await self.meta_mysql_repository.insert_meta_columns(all_columns)
                logger.info("表元数据插入MySQL完成")
                
                # 处理Qdrant向量数据写入
                logger.debug("开始处理Qdrant向量数据")
                await self._process_qdrant_data(all_columns)
                logger.info("Qdrant列向量数据写入完成")
                
                # 处理Elasticsearch值数据写入
                logger.debug("开始处理Elasticsearch值数据")
                inserted_count = await self._process_es_value_data(app_config)
                logger.info(f"Elasticsearch值数据写入完成，共插入 {inserted_count} 条记录")

            if app_config.metrics:
                logger.info("开始处理指标数据")
                # 处理指标数据
                metric_infos, column_metrics = await self._process_metric_data(app_config)
                logger.info(f"指标数据处理完成: {len(metric_infos)} 个指标, {len(column_metrics)} 个列指标关联")
                
                # 批量插入指标和列指标关联数据
                logger.debug("开始插入指标数据到MySQL")
                await self.meta_mysql_repository.insert_meta_metrics(metric_infos)
                await self.meta_mysql_repository.insert_meta_column_metrics(column_metrics)
                logger.info("指标数据插入MySQL完成")

                # 处理Qdrant向量数据写入
                logger.debug("开始处理指标Qdrant向量数据")
                await self._process_metric_qdrant_data(metric_infos)
                logger.info("Qdrant指标向量数据写入完成")

            logger.info("元数据知识图谱构建完成")
            
        except Exception as e:
            logger.error(f"构建元数据知识图谱失败: {str(e)}")
            raise
    async def _process_metadata(self, app_config: 'MetaConfig') -> tuple[list['TableInfo'], list['ColumnInfo']]:
        """处理元数据（表和列信息）
        
        Args:
            app_config: 元数据配置对象
            
        Returns:
            tuple: (表信息列表, 列信息列表)
        """
        logger.debug(f"开始处理元数据，共 {len(app_config.tables)} 个表")
        tables: list['TableInfo'] = []  # 用于收集所有TableInfo对象
        all_columns: list['ColumnInfo'] = []  # 用于收集所有ColumnInfo对象

        try:
            # 遍历配置文件中的每个表信息
            for table_info in app_config.tables:
                logger.debug(f"处理表: {table_info.name}")
                
                # 尝试从数据库中获取已存在的MetaTable对象
                existing_meta_table = await self.meta_mysql_repository.get_meta_table_by_id(table_info.name)
                # 幂等判断
                if existing_meta_table:
                    logger.debug(f"表 {table_info.name} 已存在，执行更新操作")
                    # 如果存在，则将ORM模型转换为实体类并更新属性
                    meta_table = TableInfo.from_orm(existing_meta_table)
                    meta_table.name = table_info.name
                    meta_table.role = table_info.role
                    meta_table.description = table_info.description
                    # 如果需要，还可以添加对其他字段的更新
                else:
                    logger.debug(f"表 {table_info.name} 不存在，创建新表")
                    # 如果不存在，则创建新的TableInfo实例
                    meta_table = TableInfo(
                        id=table_info.name,
                        name=table_info.name,
                        role=table_info.role,
                        description=table_info.description,
                    )
                # 将（更新后的或新创建的）TableInfo对象添加到列表中
                tables.append(meta_table)

                # 优化：一次性获取当前表所有列的详细信息，减少数据库交互
                logger.debug(f"获取表 {table_info.name} 的列详细信息")
                table_columns_details: dict[str, dict[str, Any]] = await self.dw_mysql_repository.get_table_columns_details(table_info.name)
                logger.debug(f"表 {table_info.name} 共有 {len(table_columns_details)} 个列")

                # 遍历表中的每个列信息
                for column_info in table_info.columns:
                    column_id = f"{table_info.name}_{column_info.name}"
                    logger.debug(f"处理列: {column_id}")
                    
                    # 尝试从数据库中获取已存在的MetaColumn对象
                    existing_meta_column = await self.meta_mysql_repository.get_meta_column_by_id(column_id)

                    column_detail = table_columns_details.get(column_info.name, {})
                    column_type = column_detail.get('type')
                    column_examples = column_detail.get('examples', [])
                    
                    # 幂等判断
                    if existing_meta_column:
                        logger.debug(f"列 {column_id} 已存在，执行更新操作")
                        # 如果存在，则将ORM模型转换为实体类并更新属性
                        meta_column = ColumnInfo.from_orm(existing_meta_column)
                        meta_column.table_id = table_info.name
                        meta_column.name = column_info.name
                        meta_column.type = column_type
                        meta_column.role = column_info.role
                        meta_column.examples = column_examples
                        meta_column.description = column_info.description
                        meta_column.alias = column_info.alias
                        # 如果需要，还可以添加对其他字段的更新
                    else:
                        logger.debug(f"列 {column_id} 不存在，创建新列")
                        # 如果不存在，则创建新的ColumnInfo实例
                        meta_column = ColumnInfo(
                            id=column_id,
                            table_id=table_info.name,
                            name=column_info.name,
                            type=column_type,  # 使用获取到的列类型
                            role=column_info.role,
                            examples=column_examples,  # 使用获取到的列示例值
                            description=column_info.description,
                            alias=column_info.alias,
                        )
                    # 将（更新后的或新创建的）ColumnInfo对象添加到列表中
                    all_columns.append(meta_column)
            
            logger.info(f"元数据处理完成: {len(tables)} 个表, {len(all_columns)} 个列")
            return tables, all_columns
            
        except Exception as e:
            logger.error(f"处理元数据失败: {str(e)}")
            raise

    async def _process_qdrant_data(self, all_columns: list['ColumnInfo']) -> None:
        """处理Qdrant向量数据写入
        
        Args:
            all_columns: 列信息列表
        """
        logger.debug(f"开始处理Qdrant向量数据，共 {len(all_columns)} 个列")
        
        try:
            # 确保集合存在
            logger.debug("确保Qdrant集合存在")
            await self.column_qdrant_repository.ensure_collection_exists("column_info_collection")
            
            point: list[dict] = []
            total_points = 0
            
            for column in all_columns:
                # 为列名创建向量点
                point.append({
                    "id": uuid.uuid4(),
                    'embedding_text': column.name,
                    'payload': asdict(column)
                })
                total_points += 1
                
                # 为列描述创建向量点（如果有描述）
                if column.description:
                    point.append({
                        "id": uuid.uuid4(),
                        'embedding_text': column.description,
                        'payload': asdict(column)
                    })
                    total_points += 1
                
                # 为别名创建向量点（如果有别名）
                if column.alias:
                    for alias in column.alias:
                        point.append({
                            "id": uuid.uuid4(),
                            'embedding_text': alias,
                            'payload': asdict(column)
                        })
                        total_points += 1
            
            logger.debug(f"向量点生成完成，共 {total_points} 个向量点")
            
            # 生成向量嵌入
            embedding_texts = [p['embedding_text'] for p in point]
            embeddings_size = 20 
            embeddings: list[list[float]] = []
            
            logger.debug("开始生成向量嵌入")
            for i in range(0, len(embedding_texts), embeddings_size):
                embedding_text_batch = embedding_texts[i:i+embeddings_size]
                logger.debug(f"处理第 {i//embeddings_size + 1} 批嵌入数据，共 {len(embedding_text_batch)} 个文本")
                batch_embedding_text = await self.embedding_client_manager.get_embeddings(embedding_text_batch)
                embeddings.extend(batch_embedding_text)
            
            # 提取ID和payload
            ids = [p['id'] for p in point]    
            payloads = [p['payload'] for p in point]
            
            # 写入Qdrant
            logger.debug("开始写入Qdrant向量数据")
            await self.column_qdrant_repository.upsert(ids, embeddings, payloads)
            logger.info(f"Qdrant向量数据写入完成，共写入 {len(point)} 个向量点")
            
        except Exception as e:
            logger.error(f"处理Qdrant向量数据失败: {str(e)}")
            raise

    async def _process_es_value_data(self, app_config: 'MetaConfig') -> int:
        """处理Elasticsearch值数据写入
        
        Args:
            app_config: 元数据配置对象
            
        Returns:
            int: 成功插入的记录数量
        """
        # 确保索引存在
        await self.value_es_repository.ensure_index_exists("value_index")
        
        # 值数据收集（使用ValueESRepository的批量处理功能）
        values: list[ValueInfo] = []
        
        for table in app_config.tables:
            for column in table.columns:
                if column.sync:
                    # 获取列值数据
                    list_value = await self.dw_mysql_repository.get_column_value(table.name, column.name, 100000)
                    
                    # 收集值数据
                    for value in list_value:
                        values.append(ValueInfo(
                            id=f"{table.name}_{column.name}_{value}",
                            value=str(value),  # 确保值为字符串
                            column_id=f"{table.name}_{column.name}"
                        ))
        
        # 调用ValueESRepository的批量插入功能（自动分批处理）
        if values:
            total_inserted = await self.value_es_repository.insert_values(values)
            logger.info(f"值数据插入完成，共插入 {total_inserted} 条记录")
            return total_inserted
        else:
            logger.warning("没有值数据需要插入")
            return 0

    async def _process_metric_data(self, app_config: 'MetaConfig') -> tuple[list['MetricInfo'], list['ColumnMetric']]:
        """处理指标数据
        
        Args:
            app_config: 元数据配置对象
            
        Returns:
            tuple: (指标信息列表, 列指标关联列表)
        """
        metric_infos: list['MetricInfo'] = []
        column_metrics: list['ColumnMetric'] = []
        
        for metric_config in app_config.metrics:
            # 创建指标信息
            metric_info = MetricInfo(
                id=metric_config.name,
                name=metric_config.name,
                description=metric_config.description,
                alias=metric_config.alias,
                relevant_columns=metric_config.relevant_columns,
            )
            metric_infos.append(metric_info)
            
            # 创建列指标关联
            if metric_config.relevant_columns:
                for column in metric_config.relevant_columns:
                    column_metrics.append(
                        ColumnMetric(
                            metric_id=metric_config.name,
                            column_id=column,
                        )
                    )
        
        return metric_infos, column_metrics

    async def _process_metric_qdrant_data(self, metric_infos: list['MetricInfo']) -> None:
        """处理指标Qdrant向量数据写入
        
        Args:
            metric_infos: 指标信息列表
        """
        logger.debug(f"开始处理指标Qdrant向量数据，共 {len(metric_infos)} 个指标")
        
        try:
            # 确保集合存在
            logger.debug("确保指标Qdrant集合存在")
            await self.metric_qdrant_repository.ensure_collection_exists("metric_info_collection")
            
            point: list[dict] = []
            total_points = 0
            
            for metric in metric_infos:
                # 为指标名称创建向量点
                point.append({
                    "id": uuid.uuid4(),
                    'embedding_text': metric.name,
                    'payload': asdict(metric)
                })
                total_points += 1
                
                # 为指标描述创建向量点（如果有描述）
                if metric.description:
                    point.append({
                        "id": uuid.uuid4(),
                        'embedding_text': metric.description,
                        'payload': asdict(metric)
                    })
                    total_points += 1
                
                # 为别名创建向量点（如果有别名）
                if metric.alias:
                    for alias in metric.alias:
                        point.append({
                            "id": uuid.uuid4(),
                            'embedding_text': alias,
                            'payload': asdict(metric)
                        })
                        total_points += 1
            
            logger.debug(f"指标向量点生成完成，共 {total_points} 个向量点")
            
            # 生成向量嵌入
            embedding_texts = [p['embedding_text'] for p in point]
            embeddings_size = 20 
            embeddings: list[list[float]] = []
            
            logger.debug("开始生成指标向量嵌入")
            for i in range(0, len(embedding_texts), embeddings_size):
                embedding_text_batch = embedding_texts[i:i+embeddings_size]
                logger.debug(f"处理第 {i//embeddings_size + 1} 批指标嵌入数据，共 {len(embedding_text_batch)} 个文本")
                batch_embedding_text = await self.embedding_client_manager.get_embeddings(embedding_text_batch)
                embeddings.extend(batch_embedding_text)
            
            # 提取ID和payload
            ids = [p['id'] for p in point]    
            payloads = [p['payload'] for p in point]
            
            # 写入Qdrant
            logger.debug("开始写入指标Qdrant向量数据")
            await self.metric_qdrant_repository.upsert(ids, embeddings, payloads)
            logger.info(f"指标Qdrant向量数据写入完成，共写入 {len(point)} 个向量点")
            
        except Exception as e:
            logger.error(f"处理指标Qdrant向量数据失败: {str(e)}")
            raise

    def get_meta_knowledge(self, meta_knowledge_id: int):
        pass

if __name__ == '__main__': # This block is still problematic. It should be handled in bulid_meta_knowledge.py
    pass
