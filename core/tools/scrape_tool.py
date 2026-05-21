import requests
import trafilatura
from typing import Optional
from langchain_core.tools import tool
from core.logging.logger import get_logger
from core.utils import write_debug_file, process_and_store_long_content
from core.config.settings import settings


# 取得日誌記錄器
logger = get_logger(__name__)

def _scrape_static(url: str) -> Optional[str]:
    """使用 trafilatura 進行輕量級靜態抓取"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            logger.info("✅ 成功下載網頁內容，正在進行靜態萃取...")
            return trafilatura.extract(downloaded)
        return None
    except Exception as e:
        logger.error(f"⚠️ 靜態抓取發生錯誤：{e}")
        return None

def _scrape_dynamic(url: str) -> Optional[str]:
    """使用 Jina Reader API 處理動態渲染網頁 (SPA)"""
    try:
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url, timeout=settings.request_timeout)
        if response.status_code == 200:
            logger.info("✅ 成功透過 Jina API 獲取動態網頁 Markdown 內文")
            return response.text
        else:
            logger.warning(f"⚠️ Jina API 回傳錯誤碼：{response.status_code}")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"⚠️ Jina API 請求超時 (超過 {settings.request_timeout} 秒)")
        return None
    except Exception as e:
        logger.error(f"⚠️ Jina API 請求發生錯誤：{e}")
        return None

@tool
def scrape_webpage(url: str, title: str = "", summary: str = "") -> str:
    """
    網頁抓取工具，輸入有效 url 以提取完整內文。
    你可以在已知網頁標題與摘要時，傳入 title 與 summary，這將有助於後續 RAG 記憶庫的檢索。
    工具已內建自動判斷機制：會優先嘗試高速的靜態抓取，若遇阻擋或動態網頁 (SPA)，會自動切換為無頭瀏覽器動態抓取。
    """
    logger.info(f"🕸️ 正在抓取內文：{url} | 模式：自動 (先靜態後動態)")
    
    # 第一步：嘗試輕量級靜態抓取
    content = _scrape_static(url)
    
    # 自動降級判斷：若抓取失敗，或內文字數過少（常發生於 JavaScript 阻擋頁面）
    if not content or len(content.strip()) < 100:
        logger.warning("⚠️ 靜態抓取失敗或內容過少，自動切換為動態抓取模式 (Jina API)...")
        content = _scrape_dynamic(url)

    if content:
        write_debug_file("debug_scraped", url, content)
        return process_and_store_long_content(url, content, title, summary)
    
    return "無法抓取該網頁的內容。該網頁可能設有強烈的反爬蟲機制，請換一個網址嘗試。"