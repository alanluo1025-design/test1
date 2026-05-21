# logic/workflow.py
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from logic.agents import create_agent_node, DEFAULT_TOOLS

class AgentWorkflow:
    def __init__(self):
        self.app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(state_schema=MessagesState)
        
        # 建立節點 (Nodes)
        agent_node = create_agent_node()
        tool_node = ToolNode(DEFAULT_TOOLS)

        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node) 
        
        # 定義邊界與路由
        workflow.add_edge(START, "agent")
        
        # 讓 LangGraph 自動判斷是要呼叫工具，還是結束對話
        workflow.add_conditional_edges("agent", tools_condition)
        workflow.add_edge("tools", "agent")
        
        # 綁定記憶體並編譯
        checkpointer = InMemorySaver()
        return workflow.compile(checkpointer=checkpointer)

    def chat(self, message: str, thread_id: str = "default"):
        """對外開放的聊天接口"""
        config = {"configurable": {"thread_id": thread_id}}
        result = self.app.invoke({"messages": [HumanMessage(content=message)]}, config)
        
        # 處理某些模型 (如 Gemini) 會回傳 list[dict] 格式的 content
        final_content = result["messages"][-1].content
        if isinstance(final_content, list):
            text_blocks = [block.get("text", "") for block in final_content if isinstance(block, dict) and "text" in block]
            return "\n".join(text_blocks)
            
        return final_content