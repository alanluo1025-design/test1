from .search_tool import search_web, search_news, search_academic
from .scrape_tool import scrape_webpage
from .rag_tool import search_knowledge_base, save_to_knowledge_base
from .pdf_tool import scrape_pdf

# 將所有工具打包，方便 Agent 統一載入
ALL_TOOLS = [
    search_web, search_news, search_academic, 
    scrape_webpage, search_knowledge_base, save_to_knowledge_base, scrape_pdf
]

__all__ = [
    "search_web", "search_news", "search_academic", 
    "scrape_webpage", "search_knowledge_base", "save_to_knowledge_base", "scrape_pdf",
    "ALL_TOOLS"
]
