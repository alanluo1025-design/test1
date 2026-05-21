from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API 金鑰 (請於 .env 中設定)
    google_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    nvidia_api_key: Optional[str] = None
    bot_token: Optional[str] = None

    # LLM 模型設定
    llm_provider: str = "nvidia"
    gemini_model: str = "gemini-flash-latest"
    nvidia_model: str = "nvidia/nemotron-3-super-120b-a12b"
    ollama_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"

    # 關聯式資料庫
    database_url: str = "sqlite:///./data/app.db"   # 生產環境改為 postgresql://...

    # RAG 向量資料庫 (ChromaDB)
    db_path: str = "./core/ai_agent_db"
    embedding_model_name: str = "BAAI/bge-base-zh-v1.5"
    rerank_model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    rag_threshold: int = 30000

    # 搜尋與爬蟲設定
    news_domains: List[str] = [
        "ithome.com.tw", "bnext.com.tw", "inside.com.tw", "technice.com.tw",
        "digitimes.com.tw", "techcrunch.com", "theverge.com", "bloomberg.com"
    ]
    academic_domains: List[str] = [
        "arxiv.org", "scholar.google.com", "semanticscholar.org", "ieeexplore.ieee.org"
    ]
    # 爬蟲以時間窗口為單位，而非固定筆數
    # 抓「最近 crawl_window_hours 小時內」發布的文章，自然適應當日新聞量多寡
    crawl_window_hours: int = 6       # 每次爬蟲涵蓋的時間範圍（小時）
    crawl_max_per_topic: int = 50     # 單一主題單次上限，防止爆發日 API 費用失控

    # 通用系統設定
    request_timeout: int = 15
    save_debug_files: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # 忽略 .env 中多餘的變數
    )

# 初始化全域設定實例
settings = Settings()
