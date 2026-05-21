from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.db import init_db
from core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 伺服器啟動，初始化資料庫...")
    init_db()
    logger.info("✅ 資料庫初始化完成")
    yield
    logger.info("🛑 伺服器關閉")


app = FastAPI(
    title="AI 技術洞察平台",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
