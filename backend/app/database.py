from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

# 数据库路径（使用绝对路径）
DB_PATH = "/mnt/c/SearchMenu/backend/search_menu.db"

# 确保目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 数据库连接字符串（使用 SQLite）
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # SQLite 需要这个参数
    echo=False  # 设为 True 可看到 SQL 执行语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话（用于 FastAPI 依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
