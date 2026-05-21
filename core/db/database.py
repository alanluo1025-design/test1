from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config.settings import settings


engine = create_engine(
    settings.database_url,
    # SQLite 多執行緒需要關閉此限制；PostgreSQL 不需要此參數
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依賴注入用的 DB Session 產生器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """建立所有資料表（開發初始化用）"""
    from core.db import models  # noqa: F401 — 觸發模型註冊
    Base.metadata.create_all(bind=engine)
