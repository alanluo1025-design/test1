from logic.workflow import AgentWorkflow
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def main():
    agent = AgentWorkflow()
    console.rule("🤖 AI代理人已上線", style="bold cyan")
    
    while True:
        try:
            user_input = input("請輸入你的指令（或輸入 'exit' 離開）：\nYou -> ")
            if user_input.lower() == "exit":
                print("👋 Agent 已關閉，再見！")
                break
            
            console.rule("⏳ 正在思考", style="yellow")
            print("⏳ Agent 正在自主思考與執行任務中 (這可能需要幾十秒，請稍候)...\n")
            
            # 呼叫 chat()，LangGraph 會自動在內部進行 思考->呼叫工具->再思考 的迴圈
            final_answer = agent.chat(user_input)
            
            # 用 Rich 美化輸出
            console.rule("🧠 最終回覆", style="bold green")
            md = Markdown(final_answer)
            console.print(md)
            console.rule(style="dim")
    
        except Exception as e:
            console.print(f"❌ 流程中斷：{e}", style="bold red")

if __name__ == "__main__":
    main()