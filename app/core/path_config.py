"""
路径配置模块 - 自动处理Python路径
"""

import os
import sys

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 添加项目根目录到Python路径
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 定义常用路径
APP_DIR = os.path.join(PROJECT_ROOT, "app")
AGENT_DIR = os.path.join(APP_DIR, "agent")
NODES_DIR = os.path.join(AGENT_DIR, "nodes")
CONF_DIR = os.path.join(APP_DIR, "conf")
REPOSITORIES_DIR = os.path.join(APP_DIR, "repositories")
SERVICE_DIR = os.path.join(APP_DIR, "service")

# 导出路径常量
__all__ = [
    "PROJECT_ROOT",
    "APP_DIR", 
    "AGENT_DIR",
    "NODES_DIR",
    "CONF_DIR",
    "REPOSITORIES_DIR",
    "SERVICE_DIR"
]