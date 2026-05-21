"""內容處理工具模塊 - 用於長文本處理與 RAG 存儲"""

from core.logging.logger import get_logger
from core.rag.service import save_embeddings
from core.config.settings import settings

logger = get_logger(__name__)


def process_and_store_long_content(
    source: str, content: str, title: str = "", summary: str = ""
) -> str:
    """
    處理抓取到的內容：如果過長，則組合標題與摘要後存入 RAG 記憶庫，並回傳精簡版內文。
    
    當內容長度超過 rag_threshold 設定時，自動觸發 RAG 存儲機制：
    1. 組合 title + summary + 完整內容
    2. 存入向量資料庫（ChromaDB）
    3. 返回內容前 1500 字 + 提示信息
    
    Args:
        source: 內容來源（URL 或文件名）
        content: 完整的文章內容
        title: 文章標題（可選）
        summary: 文章摘要（可選）
        
    Returns:
        若內容不超過 threshold，直接返回原內容；
        若超過 threshold，返回精簡版（前 1500 字 + 提示）
    """
    if len(content) <= settings.rag_threshold:
        return content
        
    logger.info(f"💾 內容過長 ({len(content)} 字)，正在存入 RAG 記憶庫...")
    
    # 組合高濃度的檢索片段
    enhanced_content = ""
    if title or summary:
        enhanced_content += f"【標題】{title}\n"
        enhanced_content += f"【來源】{source}\n"
        enhanced_content += f"【摘要】{summary}\n\n"
        enhanced_content += "【全文開始】\n"
        
    enhanced_content += content
    
    save_embeddings(enhanced_content, source_url_or_name=source)
    
    return content[:1500] + f"\n\n... (⚠️ 提醒：本文長達 {len(content)} 字。為了節省系統資源，已將「全文」完整存入大腦記憶庫！如果這 1500 字的片段不足以回答你的問題，請立刻使用 `search_knowledge_base` 工具來檢索這篇文章的後續細節。)"
