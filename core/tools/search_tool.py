from typing import Literal, Optional
from langchain_core.tools import tool
from tavily import TavilyClient
from core.logging.logger import get_logger
from core.config.settings import settings


# 取得日誌記錄器
logger = get_logger(__name__)

# 回復為原本的立即初始化
client = TavilyClient(api_key=settings.tavily_api_key)

def _format_search_results(response: dict) -> str:
    """內部輔助函式：將 Tavily 搜尋結果格式化為 Agent 易讀的字串"""
    if not response or not response.get("results"):
        return "目前搜尋不到符合條件的最新結果，請嘗試其他關鍵字或放寬搜尋條件。"
    
    formatted_results = "找到以下搜尋結果，請根據摘要選擇最合適的網址進行爬蟲：\n\n"
    summary_logs = []
    
    for i, result in enumerate(response["results"], start=1):
        formatted_results += f"【結果 {i}】\n"
        formatted_results += f"標題：{result['title']}\n"
        formatted_results += f"網址：{result['url']}\n"
        formatted_results += f"摘要：{result['content']}\n"
        formatted_results += "-" * 30 + "\n"
        summary_logs.append(f"[{i}] {result.get('title', '無標題')}")

    logger.info(f"📊 搜尋完成，找到 {len(response['results'])} 筆選項清單交給 Agent 評估：{', '.join(summary_logs)}")
    return formatted_results

def _handle_search_error(e: Exception, search_name: str) -> str:
    """內部輔助函式：精細化處理搜尋錯誤，給予 Agent 更明確的指示"""
    error_str = str(e).lower()
    if "api key" in error_str or "unauthorized" in error_str or "401" in error_str:
        msg = f"{search_name}失敗：Tavily API 金鑰無效或遺失。請檢查環境變數。"
    elif "limit" in error_str or "quota" in error_str or "429" in error_str:
        msg = f"{search_name}失敗：搜尋 API 額度已用盡。請告知使用者，並改用其他不需 API 的工具或直接回答。"
    elif "timeout" in error_str or "connection" in error_str:
        msg = f"{search_name}失敗：搜尋服務連線超時，請稍後重試。"
    else:
        msg = f"{search_name}過程中發生未知的錯誤：{str(e)}"
        
    logger.error(f"❌ {msg}")
    return msg

@tool
def search_web(query: str, time_range: Optional[Literal["day", "week", "month", "year"]] = None) -> str:
    """
    一般網頁搜尋工具。適用於：一般知識搜尋、名詞解釋、技術教學與官方文件。
    - 請提取核心關鍵字進行搜尋。
    - 若需要確保技術資訊正確性，可在關鍵字中加入 "official documentation" 或指定技術的官方名稱。
    """
    try:
        base_config = {"query": query, "search_depth": "basic", "max_results": settings.search_max_results}
        if time_range:
            base_config["time_range"] = time_range
            
        logger.info(f"🔍 [一般搜尋] 關鍵字：{query} | 時效：{time_range or '無限制'}")
        response = client.search(**base_config)
        return _format_search_results(response)
    except Exception as e:
        return _handle_search_error(e, "一般搜尋")

@tool
def search_news(query: str, time_range: Optional[Literal["day", "week", "month", "year"]] = "week") -> str:
    """
    新聞搜尋工具。適用於：突發事件、時事、產業最新動態。
    預設搜尋時間範圍為一週內(week)，會優先從權威新聞網域擷取資訊。
    """
    try:
        base_config = {
            "query": query,
            "search_depth": "basic",
            "max_results": settings.search_max_results,
            "topic": "news",
            "include_domains": settings.news_domains,
            "time_range": time_range
        }
        logger.info(f"📰 [新聞搜尋] 關鍵字：{query} | 時效：{time_range}")
        response = client.search(**base_config)
        return _format_search_results(response)
    except Exception as e:
        return _handle_search_error(e, "新聞搜尋")

@tool
def search_academic(query: str, time_range: Optional[Literal["day", "week", "month", "year"]] = None) -> str:
    """
    學術搜尋工具。適用於：尋找論文、學術資源或技術白皮書。
    會採用深度搜尋(advanced)並限制在學術網域。
    """
    try:
        base_config = {
            "query": query,
            "search_depth": "advanced",
            "max_results": settings.search_max_results,
            "include_domains": settings.academic_domains
        }
        if time_range:
            base_config["time_range"] = time_range
            
        logger.info(f"🎓 [學術搜尋] 關鍵字：{query} | 時效：{time_range or '無限制'}")
        response = client.search(**base_config)
        return _format_search_results(response)
    except Exception as e:
        return _handle_search_error(e, "學術搜尋")
