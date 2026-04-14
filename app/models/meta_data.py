import sys
import os
from sqlalchemy.orm import declarative_base

# Add project root to Python path (if not already handled elsewhere)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

Base = declarative_base()

# 注意：这里不再导入具体的模型类，以避免循环导入
# 模型类应该在需要时单独导入
