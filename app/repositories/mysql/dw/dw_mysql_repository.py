import re
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# 导入 DateInfoState
from app.agent.state import DateInfoState

class DWMySQLRepository:
    """
    数据仓库 MySQL 存储库。
    负责与数据仓库 MySQL 数据库进行交互。
    """
    def __init__(self,session: AsyncSession) -> None:
        """
        初始化 DWMySQLRepository。

        Args:
            session: SQLAlchemy 异步会话。
        """
        self.session: AsyncSession = session

    def _quote_identifier(self, identifier: str) -> str:
        """
        引用 MySQL 标识符以防止 SQL 注入。
        确保标识符只包含字母数字字符和下划线。
        """
        if not re.fullmatch(r'^[a-zA-Z0-9_]+$', identifier):
            raise ValueError(f"无效的标识符: {identifier}。包含不允许的字符。")
        return f"`{identifier}`"

    async def get_column_type(self, table_name: str, column_name: str) -> Optional[str]:
        """
        从数据仓库中获取指定表的指定列的数据类型。

        Args:
            table_name (str): 表名称。
            column_name (str): 列名称。

        Returns:
            Optional[str]: 列的数据类型字符串，如果未找到则返回 None。
        """
        query = text(f"""
            SELECT DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table_name
            AND COLUMN_NAME = :column_name;
        """
        )
        result = await self.session.execute(query, {"table_name": table_name, "column_name": column_name})
        return result.scalar_one_or_none()

    async def get_column_value(self, table_name: str, column_name: str, limit: int = 10) -> List[str]:
        """
        从数据仓库中获取指定表的指定列的示例值。

        Args:
            table_name (str): 表名称。
            column_name (str): 列名称。
            limit (int): 获取的示例值数量。

        Returns:
            List[str]: 列的示例值列表。
        """
        # 验证并引用表名和列名以防止 SQL 注入
        quoted_table_name = self._quote_identifier(table_name)
        quoted_column_name = self._quote_identifier(column_name)

        query = text(f"SELECT {quoted_column_name} FROM {quoted_table_name} LIMIT :limit;")
        result = await self.session.execute(query, {"limit": limit})
        return [str(row[0]) for row in result.fetchall()]

    async def get_table_columns_details(self, table_name: str, sample_limit: int = 10) -> Dict[str, Dict[str, Any]]:
        """
        一次性从数据仓库中获取指定表的所有列的详细信息（包括类型和示例值）。

        Args:
            table_name (str): 表名称。
            sample_limit (int): 获取示例值的数量。

        Returns:
            Dict[str, Dict[str, Any]]: 字典，键为列名，值为包含 'type' 和 'examples' 的字典。
        """
        # 1. 获取所有列名和类型
        query_types = text(f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table_name;
        """
        )
        
        column_details: Dict[str, Dict[str, Any]] = {}
        async with self.session as session:
            result_types = await session.execute(query_types, {"table_name": table_name})
            
            # 使用 await self.get_column_value 来获取每个列的示例值
            # 这种方式虽然会产生 N 次 get_column_value 调用，但比在 service 层多次查询要好，
            # 并且 get_column_value 内部已经处理了 SQL 注入防护。
            for row in result_types.fetchall():
                column_name = row.COLUMN_NAME
                data_type = row.DATA_TYPE
                
                # 获取示例值
                examples = await self.get_column_value(table_name, column_name, sample_limit)
                
                column_details[column_name] = {
                    "type": data_type,
                    "examples": examples
                }
        return column_details
    async def get_db_info(self):
        """
        从数据仓库中获取数据库信息。
        """
        sql = "select version()"
        result = await self.session.execute(text(sql))
        version = result.scalar_one_or_none()
        dialect = self.session.bind.dialect.name
        return {"version": version, "dialect": dialect}
    async def validate_sql(self, sql: str):
        sql = f"explain {sql}"
        await self.session.execute(text(sql))

    
    async def run_sql(self, sql: str):
        # 移除 SQL 中的注释（LLM 生成的 SQL 可能包含注释）
        import re
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        sql = sql.strip()
        
        result = await self.session.execute(text(sql))
        rows = [dict(row._mapping) for row in result.fetchall()]
        return rows
