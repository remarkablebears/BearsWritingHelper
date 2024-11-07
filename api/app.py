import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

# 不再使用 dotenv，直接從環境變數中獲取值
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 建立 Flask 應用程式
app = Flask(__name__)

# LINE Bot Webhook 路由
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    
    # 自定義的處理邏輯，例如檢查特定訊息
    if user_message in ["請幫我評估", "Please help me evaluate"]:
        response_message = get_evaluation()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_message)
        )
    else:
        # 預設回應
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我不太明白您的意思，可以輸入 '請幫我評估' 來貼上你寫好的內容喔！I don't quite understand what you mean. You can type 'Please help me evaluate' to paste your written content!")
        )

# 呼叫 Webhook 取得寫作評估
def get_evaluation():
    webhook_url = "https://bears-writing-helper.vercel.app/callback"
    try:
        response = requests.post(webhook_url, json={})
        response.raise_for_status()
        data = response.json()
        return data.get("message", "這是您的評估結果！")
    except requests.exceptions.RequestException as e:
        return f"取得評估時發生錯誤An error occurred while retrieving the evaluation.  You may also upload it to 也可以上傳到 https://poe.com/BearsWriting, Bears (brown sunglasses) will give you feedback.：{str(e)}"

# 啟動應用程式
if __name__ == "__main__":
    app.run(debug=True)
