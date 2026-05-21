import discord
import asyncio
from logic.workflow import AgentWorkflow
from core.config import settings

TOKEN = settings.bot_token

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
agent = AgentWorkflow()

@client.event
async def on_ready():
    print(f'✅ 成功登入 Discord，目前身分為 {client.user}')
    print("===============🤖AI代理人已在 Discord 上線！===============")

@client.event
async def on_message(message):
    print(f"📥 [頻道訊息] {message.author.name}: {message.content}")

    if message.author == client.user:
        return
    # 【新增邏輯】判斷是否為私人訊息 (DM)
    is_dm = isinstance(message.channel, discord.DMChannel)
    # 判斷機器人是否被標記 (伺服器群組內使用)
    is_mentioned = client.user in message.mentions
    # 檢查機器人是否被標記
    if is_dm or is_mentioned:
        print("🎯 偵測到機器人被標記，準備處理任務！")       
        # 移除訊息中的標籤 (兼容 <@ID> 與 <@!ID> 兩種格式)
        user_input = message.content.replace(f'<@{client.user.id}>', '').replace(f'<@!{client.user.id}>', '').strip()
        
        if not user_input:
            await message.channel.send("請問有什麼我可以幫忙的嗎？")
            return

        waiting_msg = await message.channel.send("⏳ Agent 正在自主思考與執行任務中 (這可能需要幾十秒，請稍候)...")
        
        try:
            # 【關鍵修正】使用 asyncio.to_thread 將同步的 AI 思考過程丟到背景執行
            print(f"🧠 [系統] 開始將任務交給 LangGraph 執行：{user_input}")
            final_answer = await asyncio.to_thread(agent.chat, user_input, str(message.author.id))
            
            if len(final_answer) > 2000:
                final_answer = final_answer[:1995] + "..."
                
            await waiting_msg.edit(content=final_answer)
            print("✅ [系統] 任務完成，已回覆至 Discord！")
            
        except Exception as e:
            error_msg = f"❌ 流程中斷：{e}"
            await waiting_msg.edit(content=error_msg)
            print(error_msg)

if __name__ == "__main__":
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ 找不到 BOT_TOKEN，請檢查 .env 檔案設定。")