# api/app.py

from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import logging

app = Flask(__name__)

# Load environment variables when running locally
if os.getenv('VERCEL_ENV') is None:
    from dotenv import load_dotenv
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# LINE Bot API and Webhook Handler initialization
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    app.logger.error("Environment variables for LINE channel token and secret are not set.")
    exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    # Get the signature from the request headers
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        app.logger.error("Signature not found in headers.")
        abort(400)

    # Get the request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Handle the webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/secret.")
        abort(400)
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        abort(500)

    return jsonify({'status': 'ok'}), 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # Echo the received message back to the user
    incoming_msg = event.message.text
    app.logger.info(f"Received message from user: {incoming_msg}")

    reply_msg = TextSendMessage(text=f"You said: {incoming_msg}")
    line_bot_api.reply_message(event.reply_token, reply_msg)

# Export the app as `app` for Vercel to detect
app = app
