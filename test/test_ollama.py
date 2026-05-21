from openai import OpenAI

# 1. 初始化連線
# base_url 強制指向你本機的 Ollama 伺服器
# api_key 在本地端不需要驗證，但套件規定要填，所以隨便塞個字串即可
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# 2. 設定模型名稱 (必須跟你剛剛下載的標籤完全一致)
MODEL_NAME = "qwen2.5:7b"

print(f"🚀 正在呼叫本地端模型 {MODEL_NAME}...\n")

# 3. 發送請求
try:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "你是一位幽默的 AI 助理，請務必使用流暢的台灣繁體中文回答。"},
            {"role": "user", "content": "你好！請用 50 個字以內簡單自我介紹，並告訴我一個關於 Python 寫程式的冷知識。"}
        ],
        temperature=0.7 # 控制創意的參數 (0.0 最死板，1.0 最天馬行空)
    )
    
    # 4. 印出結果
    reply = response.choices[0].message.content
    print("🤖 助理回覆：")
    print(reply)

except Exception as e:
    print(f"\n❌ 發生錯誤，請確認 Ollama 是否有在背景執行：{e}")