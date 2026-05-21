import hashlib
import chromadb
from typing import List
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.logging.logger import get_logger
from core.config.settings import settings

logger = get_logger(__name__)

# === 延遲載入的全域變數 (Singleton Pattern) ===
# 避免一 import 檔案就卡住載入模型
_embedding_model = None
_cross_encoder = None
_chromadb_client = None
_chromadb_collection = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"📥 正在載入 Embedding 模型 ({settings.embedding_model_name})...")
        _embedding_model = SentenceTransformer(settings.embedding_model_name)
    return _embedding_model

def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        logger.info(f"📥 正在載入 Rerank 模型 ({settings.rerank_model_name})...")
        _cross_encoder = CrossEncoder(settings.rerank_model_name)
    return _cross_encoder

def get_db_collection():
    global _chromadb_client, _chromadb_collection
    if _chromadb_collection is None:
        logger.info("💾 初始化 ChromaDB 連線...")
        _chromadb_client = chromadb.PersistentClient(path=settings.db_path)
        _chromadb_collection = _chromadb_client.get_or_create_collection(name="tech_articles")
    return _chromadb_collection


# === 核心邏輯區 ===

def split_text_into_chunks(text: str, chunk_size: int = 400, chunk_overlap: int = 50) -> List[str]:
    """
    使用 LangChain 進行智能文本切塊，保留語意重疊區域 (Overlap)，避免語意斷裂。
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "，", "、", " ", ""]
    )
    return splitter.split_text(text)

def embed_chunk(chunk: str) -> List[float]:
    model = get_embedding_model()
    embedding = model.encode(chunk, normalize_embeddings=True)
    return embedding.tolist()

def save_embeddings(text_content: str, source_url_or_name: str) -> None:
    """
    將網頁內文切塊、向量化並存入資料庫 (直接接收爬蟲回傳的字串)。
    """
    if not text_content or not text_content.strip():
        logger.warning("⚠️ 沒有資料可以寫入！")
        return
        
    # 1. 智能切塊
    chunks = split_text_into_chunks(text_content)
    if not chunks:
        return
        
    # 2. 向量化
    embeddings = [embed_chunk(c) for c in chunks]
    
    # 3. 準備 DB 寫入資料
    # 對來源網址做 Hash，避免檔名過長或包含非法字元，並用於 ID 生成
    source_hash = hashlib.md5(source_url_or_name.encode()).hexdigest()[:8]
    ids = [f"{source_hash}_chunk_{i}" for i in range(len(chunks))]
    
    metadatas = [{"source": source_url_or_name} for _ in range(len(chunks))]

    collection = get_db_collection()
    
    # 使用 upsert 防止重複爬取導致的崩潰
    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    logger.info(f"✅ 成功將 [{source_url_or_name}] 轉換為 {len(chunks)} 個記憶區塊並存入大腦！")

def retrieve(query: str, top_k: int = 10) -> List[str]:
    collection = get_db_collection()
    query_embedding = embed_chunk(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0] if results and results['documents'] else []

def rerank(query: str, retrieved_chunks: List[str], top_k: int = 3) -> List[str]:
    if not retrieved_chunks:
        return []

    model = get_cross_encoder()
    pairs = [(query, chunk) for chunk in retrieved_chunks]
    scores = model.predict(pairs)

    scored_chunks = list(zip(retrieved_chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return [chunk for chunk, _ in scored_chunks][:top_k]

def delete_by_source(source_url_or_name: str) -> None:
    """
    從資料庫中刪除特定來源（如網址或檔名）的所有記憶區塊。
    """
    collection = get_db_collection()
    try:
        collection.delete(where={"source": source_url_or_name})
        logger.info(f"🗑️ 成功刪除來源 [{source_url_or_name}] 的所有相關記憶！")
    except Exception as e:
        logger.error(f"❌ 刪除來源 [{source_url_or_name}] 失敗: {str(e)}")

def clear_all_data() -> None:
    """
    清空 ChromaDB 資料庫中的所有內容。
    """
    try:
        global _chromadb_client, _chromadb_collection
        get_db_collection() # 確保 client 與 collection 已被初始化
            
        _chromadb_client.delete_collection(name="tech_articles")
        _chromadb_collection = _chromadb_client.get_or_create_collection(name="tech_articles")
        logger.info("💥 成功清空所有記憶庫資料！")
    except ValueError:
        logger.warning("⚠️ 記憶庫集合可能已經不存在，無需清空。")
    except Exception as e:
        logger.error(f"❌ 清空記憶庫失敗: {str(e)}")

def search_knowledge_base_logic(query: str, top_k: int = 3) -> str:
    """
    整合檢索與重排的商業邏輯，為後續封裝為 Agent @tool 做準備。
    """
    logger.info(f"🧠 從記憶庫檢索：{query}")
    docs = retrieve(query, top_k=10)
    best_docs = rerank(query, docs, top_k=top_k)
    
    if not best_docs:
        return "記憶庫中目前沒有與此問題相關的資料。"
        
    formatted_result = "以下是從資料庫中檢索到的相關背景知識：\n\n"
    for i, doc in enumerate(best_docs, 1):
        formatted_result += f"【片段 {i}】\n{doc}\n" + "-"*30 + "\n"
    return formatted_result