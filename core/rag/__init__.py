"""
core.rag - 向量搜索與 RAG 模塊

統一管理 ChromaDB、embedding、搜索和重排序相關功能。
"""

from .service import (
    get_embedding_model,
    get_cross_encoder,
    get_db_collection,
    search_knowledge_base_logic,
    split_text_into_chunks,
    save_embeddings,
    retrieve,
    rerank,
    delete_by_source,
    clear_all_data,
)

__all__ = [
    "get_embedding_model",
    "get_cross_encoder",
    "get_db_collection",
    "search_knowledge_base_logic",
    "split_text_into_chunks",
    "save_embeddings",
    "retrieve",
    "rerank",
    "delete_by_source",
    "clear_all_data",
]
