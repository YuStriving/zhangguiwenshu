import sys
import os

# 移除错误的导入语句
# from requests import compat

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# 导入必要的类型
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo
from app.agent.state import ColumnInfoState, DataAgentState, MetricInfoState, TableInfoState
from app.agent.context import DataAgentContext
from langgraph.runtime import Runtime
from app.entities.table_info import TableInfo
from app.core.log import logger


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]) -> DataAgentState:
    """信息合并节点 - 整合不同来源的数据信息
    
    功能说明:
    - 将字段信息、指标信息和取值信息进行关联整合
    - 补充缺失的字段信息（通过MySQL查询）
    - 构建表-字段的分组结构
    - 转换为数据智能体状态格式
    
    参数:
        state: DataAgentState - 数据智能体状态
        runtime: Runtime[DataAgentContext] - 运行时上下文
        
    返回:
        DataAgentState - 更新后的状态，包含整合后的表信息和指标信息
        
    处理流程:
        1. 初始化字段信息映射
        2. 处理指标相关字段（补充缺失字段）
        3. 处理字段取值（关联到对应字段）
        4. 构建表-字段分组结构
        5. 转换为状态格式
    """
    wirte = runtime.stream_writer
    wirte("开始合并信息")
    
    logger.info(
        "开始信息合并处理",
        extra={
            "method": "merge_retrieved_info",
            "retrieved_columns_count": len(state.get('retrieved_column_info', [])),
            "retrieved_metrics_count": len(state.get('retrieved_metric_info', [])),
            "retrieved_values_count": len(state.get('retrieved_value_info', []))
        }
    )
    # 获取状态中的各类信息
    retrieved_value_info :list[ValueInfo] = state['retrieved_value_info']
    retrieved_column_info :list[ColumnInfo] = state['retrieved_column_info']
    retrieved_metric_info :list[MetricInfo] = state['retrieved_metric_info']
    meta_mysql_repository = runtime.context['meta_mysql_repository']
    
    # 构建字段信息映射，便于快速查找
    retrieved_column_info_map:dict[str,ColumnInfo] = {retrieved_column.id :retrieved_column for retrieved_column in retrieved_column_info}
    
    logger.debug(
        "初始化字段信息映射",
        extra={
            "method": "merge_retrieved_info",
            "initial_columns_count": len(retrieved_column_info_map),
            "metric_count": len(retrieved_metric_info),
            "value_count": len(retrieved_value_info)
        }
    )

    # 处理指标相关字段 - 补充缺失的字段信息
    logger.debug("开始处理指标相关字段")
    for retrieved_metric in retrieved_metric_info:
        for relevant_column in retrieved_metric.relevant_columns:
            if relevant_column not in retrieved_column_info_map:
                logger.debug(
                    "补充缺失的指标相关字段",
                    extra={
                        "method": "merge_retrieved_info",
                        "metric_name": retrieved_metric.name,
                        "relevant_column_id": relevant_column
                    }
                )
                column_info:ColumnInfo = await meta_mysql_repository.get_column_by_id(relevant_column)
                retrieved_column_info_map[relevant_column] = column_info
    # 处理字段取值 - 关联取值到对应字段
    logger.debug("开始处理字段取值关联")
    for retrieved_value in retrieved_value_info:
        value = retrieved_value.value
        column_id = retrieved_value.column_id
        
        # 如果字段信息不存在，从MySQL补充
        if column_id not in retrieved_column_info_map:
            logger.debug(
                "补充缺失的取值相关字段",
                extra={
                    "method": "merge_retrieved_info",
                    "column_id": column_id,
                    "value": value
                }
            )
            column_info:ColumnInfo = await meta_mysql_repository.get_column_by_id(column_id)
            retrieved_column_info_map[column_id] = column_info
        
        # 将取值添加到字段的示例列表中（去重）
        if value not in retrieved_column_info_map[column_id].examples:
            retrieved_column_info_map[column_id].examples.append(value)
    
    logger.debug(
        "字段取值处理完成",
        extra={
            "method": "merge_retrieved_info",
            "final_columns_count": len(retrieved_column_info_map),
            "values_processed": len(retrieved_value_info)
        }
    )
    
    # 构建表-字段的分组结构
    logger.debug("开始构建表-字段分组结构")
    table_to_columns_map:dict[str,list[ColumnInfo]] = {}
    for column_info in retrieved_column_info_map.values():
        if column_info is None:
            continue
        table_id = column_info.table_id
        if table_id is None:
            continue
        if table_id not in table_to_columns_map:
            table_to_columns_map[table_id] = []
        table_to_columns_map[table_id].append(column_info)
    
    logger.debug(
        "表-字段分组构建完成",
        extra={
            "method": "merge_retrieved_info",
            "tables_count": len(table_to_columns_map),
            "total_columns": len(retrieved_column_info_map)
        }
    )
    # 强制为每个表添加主外键字段信息
    logger.debug("开始补充主外键字段信息")
    for table_id in table_to_columns_map.keys():
        key_columns:list[ColumnInfo] = await meta_mysql_repository.get_key_columns_by_table_id(table_id)
        column_ids = [column_info.id for column_info in table_to_columns_map[table_id]]
        for key_column in key_columns:
            if key_column.id not in column_ids:
                table_to_columns_map[table_id].append(key_column)

    logger.debug(
            "主外键字段信息补充完成",
            extra={
                "method": "merge_retrieved_info",
                "tables_count": len(table_to_columns_map),
                "total_columns": len(retrieved_column_info_map)
            }
        )
    table_info_list:list[TableInfoState] = []
    for table_id,column_info in table_to_columns_map.items():
        table_info:TableInfo = await meta_mysql_repository.get_table_by_id(table_id)
        columns = [ColumnInfoState(
            name = info.name,
            type = info.type,
            description = info.description,
            alias = info.alias,
            examples = info.examples,
            role = info.role
        ) for info in column_info]
        table_info_state = TableInfoState(
            name = table_info.name,
            columns = columns,
            description = table_info.description,
            role = table_info.role
        )
        table_info_list.append(table_info_state)
    
    # 转换指标信息为状态格式
    metric_info_list:list[MetricInfoState] = [MetricInfoState(
        name = metric.name,
        description = metric.description,
        relevant_columns = metric.relevant_columns,
        alias = metric.alias
    ) for metric in retrieved_metric_info]
    
    # 记录最终合并结果
    logger.info(
        "信息合并处理完成",
        extra={
            "method": "merge_retrieved_info",
            "final_tables_count": len(table_info_list),
            "final_metrics_count": len(metric_info_list),
            "total_columns_processed": len(retrieved_column_info_map)
        }
    )
    
    wirte(f"信息合并完成，共处理{len(table_info_list)}个表，{len(metric_info_list)}个指标")
    return {
        'table_infos':table_info_list,
        'metric_infos':metric_info_list
    }