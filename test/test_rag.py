import sys
import logging

from core.rag_service import (
    save_embeddings,
    search_knowledge_base_logic,
    delete_by_source,
    clear_all_data,
    get_db_collection
)

# 強制終端機輸出為 UTF-8 (解決 Windows emoji 印出報錯的問題)
sys.stdout.reconfigure(encoding='utf-8')

# 設定 logging 格式以便觀察輸出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def run_tests():
    print("=" * 60)
    print("🚀 開始測試 RAG 服務 (rag_service.py)")
    print("=" * 60)

    # 1. 清空所有資料，確保測試環境乾淨
    print("\n[測試 1] 清空資料庫...")
    clear_all_data()
    collection = get_db_collection()
    print(f"目前資料庫筆數: {collection.count()}")

    # 2. 測試存入文本
    print("\n[測試 2] 寫入測試文本...")
    test_source_1 = "https://example.com/ai-news-1"
    test_text_1 = """
    人工智慧（AI）在 2024 年取得了重大突破，特別是在自然語言處理與大型語言模型領域。
    OpenAI 發布了最新的 GPT-4o 模型，大幅提升了多模態的處理能力，不僅能處理文字，
    還能即時處理語音和影像，反應速度更快，且更具備情緒感知能力。
    這項技術預計將廣泛應用於客服機器人、虛擬助手以及自動化程式碼生成等場景。
    """

    test_source_2 = "https://example.com/space-news-1"
    test_text_2 = """
    SpaceX 星艦（Starship）今天成功完成了第五次軌道測試飛行，這標誌著人類邁向火星的一大步。
    本次任務中最令人矚目的成突破是「筷子」（Chopsticks）回收系統成功在發射台上夾住了返回的超級重型助推器。
    伊隆·馬斯克表示，這項技術將大幅降低太空發射成本，未來有望實現每天發射多次的目標。
    """
    
    save_embeddings(test_text_1, test_source_1)
    save_embeddings(test_text_2, test_source_2)
    print(f"寫入後資料庫筆數: {collection.count()}")

    # 3. 測試搜尋邏輯
    print("\n[測試 3] 測試 RAG 搜尋...")
    
    query_ai = "最新的 GPT 模型有什麼特色？"
    print(f"❓ 搜尋問題: {query_ai}")
    search_result_ai = search_knowledge_base_logic(query_ai, top_k=2)
    print(f"💡 搜尋結果:\n{search_result_ai}")

    query_space = "星艦測試的亮點是什麼？"
    print(f"\n❓ 搜尋問題: {query_space}")
    search_result_space = search_knowledge_base_logic(query_space, top_k=2)
    print(f"💡 搜尋結果:\n{search_result_space}")

    # 4. 測試依來源刪除
    print("\n[測試 4] 測試依來源刪除記憶...")
    print(f"準備刪除來源: {test_source_2}")
    delete_by_source(test_source_2)
    print(f"刪除後資料庫筆數: {collection.count()}")
    
    # 再次搜尋星艦問題，看是否還有相關資料 (預期會回答找不到或給出不相關的資料)
    print("\n再次搜尋星艦問題...")
    search_result_space_after_delete = search_knowledge_base_logic(query_space, top_k=2)
    print(f"💡 刪除後的搜尋結果:\n{search_result_space_after_delete}")

    # 5. 測試完成後清空資料庫
    print("\n[測試 5] 測試完成，還原環境 (清空資料庫)...")
    clear_all_data()
    collection = get_db_collection()
    print(f"最終資料庫筆數: {collection.count()}")

    print("\n" + "=" * 60)
    print("✅ 測試執行完畢！")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
