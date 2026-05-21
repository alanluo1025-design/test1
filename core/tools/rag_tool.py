from langchain_core.tools import tool
from core.rag.service import search_knowledge_base_logic, save_embeddings
from core.logging.logger import get_logger

logger = get_logger(__name__)

@tool
def search_knowledge_base(query: str) -> str:
    """
    記憶庫檢索工具 (RAG Knowledge Base)。
    當你需要回憶過去爬取過的長篇網頁內容，或是需要針對某個主題尋找特定背景知識時，
    請輸入明確的搜尋關鍵字 (query) 來檢索大腦記憶庫。
    """
    logger.info(f"🔍 呼叫記憶庫查詢工具，關鍵字：{query}")
    return search_knowledge_base_logic(query)

@tool
def save_to_knowledge_base(content: str, source: str) -> str:
    """
    資訊存檔工具。
    當你獲得有價值的長篇資訊、深入的分析結果，或是抓取到需要長期記憶的網頁內容時，
    請使用此工具將其存入大腦記憶庫。
    
    Args:
        content: 要存入的完整文本內容。
        source: 資訊來源的描述（例如：網址、標題或檔案名稱）。
    """
    logger.info(f"💾 呼叫記憶庫存檔工具，來源：{source}")
    try:
        save_embeddings(content, source_url_or_name=source)
        return f"SUCCESS: 成功將來自 [{source}] 的內容存入記憶庫。"
    except Exception as e:
        logger.error(f"ERROR: 存檔失敗：{str(e)}")
        return f"ERROR: 存檔過程發生錯誤：{str(e)}"
