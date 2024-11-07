import os
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 設置 LINE Bot API 和 Webhook Handler
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 建立 Flask 應用程式
app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    # 獲取簽名資訊
    signature = request.headers.get("X-Line-Signature")

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

    # 回應 LINE 平台，確認請求成功處理
    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"您說了：{user_message}")
    )

# 啟動應用程式
if __name__ == "__main__":
    app.run(debug=True)
