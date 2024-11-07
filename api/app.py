import os
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import logging
from dotenv import load_dotenv

# 建立 Flask 應用程式
app = Flask(__name__)

# 設置環境變數
# 若在本地運行則載入 .env 檔案
if os.getenv('VERCEL_ENV') is None:
    load_dotenv()

# 設置 LINE 和 OpenAI API
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    app.logger.error("Environment variables for LINE channel token and secret are not set.")
    exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 設置日誌紀錄
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# LINE Bot Webhook 路由
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        app.logger.error("Signature not found in headers.")
        abort(400)

    # 獲取請求內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證請求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/secret.")
        abort(400)
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        abort(500)

    return jsonify({'status': 'ok'}), 200

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    # 如果使用者輸入 "請幫我評估", "Please help me evaluate"，呼叫 Webhook 取得挑戰資料
    if user_message in ["請幫我評估", "Please help me evaluate"]:
        response_message = get_evaluation()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_message)
        )
    else:
        # 預設回應
        reply_msg = "我不太明白您的意思，可以輸入 '請幫我評估' 來貼上你寫好的內容喔！I’m not quite sure what you mean. You can type 'Please help me evaluate' to paste your written content!"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg)
        )

# 呼叫 Webhook 取得寫作評估
def get_evaluation():
    webhook_url = "https://bears-writing-helper.vercel.app/callback"
    try:
        response = requests.post(webhook_url, json={})
        response.raise_for_status()
        data = response.json()
        return data.get("message", "這是你的評分！This is your evaluation.")
    except requests.exceptions.RequestException as e:
        return f"取得評估時發生錯誤An error occurred while retrieving the evaluation. 請改上傳 Please upload to：https://poe.com/GrammarWithBears {str(e)}"

# 啟動應用程式
if __name__ == "__main__":
    app.run(debug=True)
