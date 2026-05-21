import os
import io
import requests
from typing import Optional
from langchain_core.tools import tool
from pypdf import PdfReader
from core.logging.logger import get_logger
from core.utils import write_debug_file, process_and_store_long_content
from core.config.settings import settings



# 取得日誌記錄器
logger = get_logger(__name__)

def _extract_text_from_pdf_stream(stream: io.BytesIO) -> Optional[str]:
    """從 Byte Stream 中解析 PDF 文字"""
    try:
        reader = PdfReader(stream)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"⚠️ 解析 PDF 時發生錯誤：{e}")
        return None

def _download_and_extract_pdf(url: str) -> Optional[str]:
    """下載網路 PDF 並解析文字"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=settings.request_timeout)
        if response.status_code == 200:
            logger.info("✅ 成功下載 PDF，正在解析內容...")
            stream = io.BytesIO(response.content)
            return _extract_text_from_pdf_stream(stream)
        else:
            logger.warning(f"⚠️ 下載 PDF 失敗，HTTP 狀態碼：{response.status_code}")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"⚠️ 下載 PDF 超時 (超過 {settings.request_timeout} 秒)")
        return None
    except Exception as e:
        logger.error(f"⚠️ 下載 PDF 時發生未預期錯誤：{e}")
        return None

def _read_local_pdf(file_path: str) -> Optional[str]:
    """讀取本地 PDF 並解析文字"""
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ 找不到本地 PDF 檔案：{file_path}")
        return None
    
    try:
        logger.info(f"✅ 找到本地 PDF，正在解析內容：{file_path}")
        with open(file_path, "rb") as f:
            stream = io.BytesIO(f.read())
            return _extract_text_from_pdf_stream(stream)
    except Exception as e:
        logger.error(f"⚠️ 讀取本地 PDF 檔案時發生錯誤：{e}")
        return None

@tool
def scrape_pdf(source: str, title: str = "", summary: str = "") -> str:
    """
    PDF 抓取工具，可輸入網路 PDF 的 URL 或本地 PDF 的檔案路徑。
    你可以在已知 PDF 標題與摘要時，傳入 title 與 summary，這將有助於後續 RAG 記憶庫的檢索。
    能將 PDF 的文字內容提取出來，方便後續分析與檢索。
    """
    logger.info(f"📄 正在處理 PDF：{source}")
    
    # 判斷是 URL 還是本地檔案
    if source.startswith("http://") or source.startswith("https://"):
        content = _download_and_extract_pdf(source)
    else:
        content = _read_local_pdf(source)
        
    if not content:
        return f"無法解析 PDF ({source})。請確認網址或檔案路徑是否正確，且 PDF 非純圖片格式。"

    # 寫入除錯紀錄
    write_debug_file("debug_scraped_pdf", source, content)
    
    return process_and_store_long_content(source, content, title, summary)
