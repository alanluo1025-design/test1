import os
import sys

# 將專案根目錄加入路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.rag_tool import save_to_knowledge_base, search_knowledge_base

def test_rag_save_and_search():
    print("[TEST] Testing RAG save tool...")
    
    test_content = "Antigravity is a powerful AI coding assistant developed by the Google DeepMind team."
    test_source = "TestDoc_001"
    
    # Test saving
    result_save = save_to_knowledge_base.invoke({"content": test_content, "source": test_source})
    print(f"Save result: {result_save}")
    
    # Test searching
    print("\n[TEST] Testing RAG search tool...")
    result_search = search_knowledge_base.invoke({"query": "Who developed Antigravity?"})
    print(f"Search result:\n{result_search}")

if __name__ == "__main__":
    test_rag_save_and_search()
