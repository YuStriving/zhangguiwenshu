from typing import List, Optional
from dataclasses import asdict
from app.core.log import logger
from app.client.es_client_manager import es_client_manager

class ValueESRepository:
    """值ES存储库类"""
    
    def __init__(self, es_client: 'AsyncElasticsearch') -> None:
        self.es_client = es_client
        self.index_name = "value_index"  # 默认索引名称

    async def ensure_index_exists(self, index_name: Optional[str] = None) -> None:
        """确保索引存在"""
        index_name = index_name or self.index_name
        await es_client_manager.ensure_index_exists(index_name)
    
    async def insert_values(self, values: List['ValueInfo'], batch_size: int = 1000) -> int:
        """插入值数据（带分批处理）
        
        Args:
            values: 值数据列表
            batch_size: 每批处理数量
            
        Returns:
            int: 成功插入的记录数
        """
        if not values:
            logger.warning("没有值数据需要插入")
            return 0
            
        total_inserted = 0
        
        # 分批处理
        for i in range(0, len(values), batch_size):
            batch = values[i:i+batch_size]
            batch_operations = []
            
            for value in batch:
                # 构建批量操作
                batch_operations.append({
                    "index": {
                        "_index": self.index_name,
                        "_id": value.id
                    }
                })
                batch_operations.append(asdict(value))
            
            # 执行批量插入
            try:
                response = await self.es_client.bulk(operations=batch_operations)
                
                # 检查批量操作结果
                if response.get('errors', False):
                    errors = [item for item in response['items'] if 'error' in item.get('index', {})]
                    logger.warning(f"批量插入中有 {len(errors)} 条记录失败")
                    
                # 统计成功插入的数量
                successful_items = [item for item in response['items'] if item.get('index', {}).get('result') == 'created']
                batch_inserted = len(successful_items)
                total_inserted += batch_inserted
                
                logger.info(f"批次 {i//batch_size + 1} 插入完成: {batch_inserted}/{len(batch)} 条记录")
                
            except Exception as e:
                logger.error(f"批次 {i//batch_size + 1} 插入失败: {e}")
                # 可以选择继续处理下一批或抛出异常
                raise
        
        logger.info(f"值数据插入完成，共插入 {total_inserted} 条记录")
        return total_inserted
    
    async def bulk_insert_values(self, value_generator, batch_size: int = 1000) -> int:
        """流式批量插入值数据（适用于大数据量）
        
        Args:
            value_generator: 值数据生成器
            batch_size: 每批处理数量
            
        Returns:
            int: 成功插入的记录数
        """
        total_inserted = 0
        current_batch = []
        
        async for value in value_generator:
            current_batch.append(value)
            
            if len(current_batch) >= batch_size:
                inserted = await self.insert_values(current_batch, batch_size)
                total_inserted += inserted
                current_batch.clear()
        
        # 处理剩余数据
        if current_batch:
            inserted = await self.insert_values(current_batch, batch_size)
            total_inserted += inserted
        
        return total_inserted



       
                                                              