# logic/agents.py
from datetime import datetime
from langchain_core.messages import SystemMessage
from logic.llm_factory import get_llm
from core.tools import ALL_TOOLS
from logic.prompts import get_system_prompt

# 定義 Agent 預設可以使用的工具清單 (從 core.tools 統一管理)
DEFAULT_TOOLS = ALL_TOOLS

def create_agent_node(tools: list = None, llm_provider: str = None, model_name: str = None):
    """
    初始化 LLM、綁定工具，並回傳給 LangGraph 使用的節點函式。
    支援依賴注入：可自訂此 Node 要使用的 tools 陣列與 LLM 模型。
    """
    active_tools = tools if tools is not None else DEFAULT_TOOLS
    
    # 透過工廠動態取得模型 (支援透過參數覆蓋 .env 預設值)
    llm = get_llm(provider=llm_provider, model_name=model_name)
    llm_with_tools = llm.bind_tools(active_tools)
    
    def agent_node(state):
        current_date = datetime.now().strftime("%Y年%m月%d日 %A")
        
        system_prompt = SystemMessage(content=get_system_prompt(current_date))
        
        # 記憶體截斷保護機制：避免爬蟲的長文本不斷累積撐爆 Context Window
        raw_messages = state["messages"]
        if len(raw_messages) > 10:
            # 往回推 10 筆，並尋找最近的一個 HumanMessage 作為安全起點。
            # 這是為了避免「剛好切在 AIMessage(ToolCall) 和 ToolMessage 之間」，導致 API 報錯
            start_idx = len(raw_messages) - 10
            for i in range(start_idx, len(raw_messages)):
                if raw_messages[i].type == "human":
                    start_idx = i
                    break
            safe_messages = raw_messages[start_idx:]
        else:
            safe_messages = raw_messages
            
        # 組合 System Prompt 與安全截斷後的對話歷史
        messages = [system_prompt] + safe_messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
        
    return agent_node