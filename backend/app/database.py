from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from pathlib import Path

# 数据库路径：优先使用环境变量，否则使用 app/ 所在目录的上一级（即 backend/ 或 /app/）
_default_db_path = str(Path(__file__).parent.parent / "search_menu.db")
DB_PATH = os.environ.get("DB_PATH", _default_db_path)

# 确保目录存在
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

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
