"""MySQL客户端管理器模块

此模块负责管理MySQL的客户端连接，提供初始化和关闭连接的功能。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.conf.app_config import DBConfig, app_config
from app.core.log import logger


class MySQLClientManager:
    """MySQL客户端管理器类
    
    负责管理MySQL的客户端连接，提供初始化和关闭连接的方法。
    """
    
    def __init__(self, config: DBConfig):
        """初始化MySQL客户端管理器
        
        参数:
            config: DBConfig - MySQL数据库配置对象
        """
        self.engine: Optional[AsyncEngine] = None
        self.Session: Optional[sessionmaker] = None
        self.config: DBConfig = config

    def _get_url(self) -> str:
        """获取MySQL数据库的URL
        
        返回:
            str - MySQL数据库的URL
        """
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
    
    async def init(self):
        """初始化MySQL客户端连接
        
        创建并初始化AsyncEngine实例，连接到配置的MySQL数据库。
        """
        self.engine = create_async_engine(
            self._get_url(),
            echo=False,  # 是否打印SQL语句
            pool_pre_ping=True,  # 连接前测试连接是否有效
            pool_size=10,  # 连接池大小，默认5
            max_overflow=20,  # 最大溢出连接数，默认10
            pool_recycle=3600,  # 连接回收时间（秒），避免连接过期
            pool_timeout=30  # 连接超时时间（秒），默认30
        )
        self.Session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def close(self):
        """关闭MySQL客户端连接
        
        关闭当前的AsyncEngine连接。
        """
        if self.engine:
            await self.engine.dispose()
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话
        
        返回:
            AsyncGenerator[AsyncSession, None] - 数据库会话生成器
        """
        if not self.Session:
            raise RuntimeError("客户端未初始化")
        
        async with self.Session() as session:
            try:
                yield session
                # 如果事务没有出现问题，提交事务
                await session.commit()
            except Exception as e:
                # 如果事务出现问题，回滚事务
                await session.rollback()
                raise e


# 创建MySQL客户端管理器实例
# 使用应用配置中的元数据库配置
mysql_meta_client_manager = MySQLClientManager(app_config.db_meta)

# 创建MySQL客户端管理器实例
# 使用应用配置中的数据仓库配置
mysql_dw_client_manager = MySQLClientManager(app_config.db_dw)


async def test():
    """测试函数，用于测试MySQL客户端
    
    测试初始化客户端、创建表、插入数据、查询数据等操作。
    """
    logger.debug("初始化MySQL客户端...")
    await mysql_meta_client_manager.init()
    logger.info("MySQL客户端初始化成功")
    
    try:
        # 测试数据
        logger.debug("获取数据库会话...")
        async for session in mysql_meta_client_manager.get_session():
            logger.debug("数据库会话获取成功")
            
            # 测试连接
            logger.debug("测试数据库连接...")
            result = await session.execute(text("SELECT 1"))
            logger.debug(f"连接测试结果: {result.scalar()}")
            
            # 测试创建表
            logger.debug("创建测试表...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    value INT NOT NULL
                )
            """))
            logger.info("测试表创建成功")
            
            # 测试插入数据
            logger.debug("插入测试数据...")
            await session.execute(
                text("INSERT INTO test_table (name, value) VALUES (:name, :value)"),
                {"name": "测试数据1", "value": 100}
            )
            await session.execute(
                text("INSERT INTO test_table (name, value) VALUES (:name, :value)"),
                {"name": "测试数据2", "value": 200}
            )
            logger.info("测试数据插入成功")
            
            # 测试查询数据
            logger.debug("查询测试数据...")
            result = await session.execute(text("SELECT * FROM test_table"))
            rows = result.all()
            logger.info(f"查询到 {len(rows)} 条数据")
            # 只在debug级别显示具体数据
            for row in rows:
                logger.debug(f"ID: {row.id}, Name: {row.name}, Value: {row.value}")
            
            # 测试使用fetchall方法
            logger.debug("使用fetchall方法查询数据...")
            result = await session.execute(text("SELECT * FROM test_table"))
            rows_fetchall = result.fetchall()
            logger.info(f"fetchall查询到 {len(rows_fetchall)} 条数据")
            # 只在debug级别显示具体数据
            for row in rows_fetchall:
                logger.debug(f"ID: {row[0]}, Name: {row[1]}, Value: {row[2]}")
            
            # 测试删除测试表
            logger.debug("删除测试表...")
            await session.execute(text("DROP TABLE IF EXISTS test_table"))
            logger.info("测试表删除成功")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
    finally:
        # 关闭客户端
        logger.debug("关闭MySQL客户端...")
        await mysql_meta_client_manager.close()
        logger.info("MySQL客户端关闭成功")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())