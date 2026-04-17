"""
环境设置脚本 - 自动配置Python路径
运行此脚本后，项目中的所有模块都可以直接导入
"""

import os
import sys

def setup_environment():
    """设置Python环境路径"""
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 添加项目根目录到Python路径
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 添加常用目录到Python路径
    app_dirs = [
        "app",
        "app/agent", 
        "app/agent/nodes",
        "app/conf",
        "app/core",
        "app/repositories",
        "app/service"
    ]
    
    for dir_name in app_dirs:
        dir_path = os.path.join(project_root, dir_name)
        if dir_path not in sys.path:
            sys.path.append(dir_path)
    
    print("[OK] 环境设置完成！")
    print(f"[DIR] 项目根目录: {project_root}")
    print(f"[INFO] Python路径包含: {len(sys.path)} 个目录")
    
    # 测试导入
    try:
        from app.conf.app_config import app_config
        from app.agent.llm import llm
        print("[OK] 测试导入成功！")
        return True
    except ImportError as e:
        print(f"[ERROR] 导入测试失败: {e}")
        return False

if __name__ == "__main__":
    setup_environment()