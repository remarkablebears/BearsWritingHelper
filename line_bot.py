# line_bot.py

from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
import os
import logging

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# LINE Bot API and Webhook Handler initialization
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# Check if the tokens are available
if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    app.logger.error("Environment variables for LINE channel token and secret are not set.")
    exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Optional: Set your specific MyGPT model ID if required
MYGPT_MODEL_ID = os.getenv('MYGPT_MODEL_ID', 'g-JiZNxTbi4')  # Replace with your specific MyGPT code or set in .env

@app.route("/callback", methods=["POST"])
def callback():
    """
    Callback function to handle incoming requests from LINE's Messaging API.
    """
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

# Event handler for text messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    Event handler for when a user sends a text message to your LINE bot.
    """
    # Get the incoming message text
    incoming_msg = event.message.text
    app.logger.info(f"Received message from user: {incoming_msg}")

    # Process the message or integrate with MyGPT model if required
    # For example, you can send the message to MyGPT and get a response
    # response = get_response_from_mygpt(incoming_msg, MYGPT_MODEL_ID)
    # reply_msg = TextSendMessage(text=response)

    # For now, we'll just echo back the received message
    reply_msg = TextSendMessage(text=f"You said: {incoming_msg}")
    line_bot_api.reply_message(event.reply_token, reply_msg)

# Function to integrate with MyGPT (if needed)
# def get_response_from_mygpt(user_message, model_id):
#     """
#     Function to get a response from the MyGPT model.
#     """
#     # Implement the API call to MyGPT here
#     # For example:
#     # response = call_mygpt_api(user_message, model_id)
#     # return response
#     pass

# Run the app
if __name__ == "__main__":
    # Use port 5000 or the port specified by the environment
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
