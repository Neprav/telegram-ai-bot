from flask import Flask, request
from message_handler import MessageHandler
import os
import json
import requests
import logging
import sys

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def load_from_gcs(bucket_name, file_name):
    """Load file from Google Cloud Storage"""
    try:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        content = blob.download_as_text(encoding="utf-8")
        return json.loads(content)
    except Exception as e:
        logging.error(f"Error loading config from GCS: {e}")
        raise

# Determine where the script is running and load configuration
is_cloud_run = os.environ.get("K_SERVICE") is not None

if is_cloud_run:
    BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    if not BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME is not set in environment variables")
    config = load_from_gcs(BUCKET_NAME, "config.json")
else:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except (ImportError, FileNotFoundError):
        BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
        if not BUCKET_NAME:
            raise ValueError("GCS_BUCKET_NAME is not set in environment variables")
        config = load_from_gcs(BUCKET_NAME, "config.json")

handler = MessageHandler(config)

TRIGGER_WORD = config.get("trigger_word")
if not TRIGGER_WORD:
    raise ValueError("trigger_word is not set in configuration")
TRIGGER_WORD = TRIGGER_WORD.lower()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set! Make sure it is set in environment variables.")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
TELEGRAM_BOT_USERNAME = None  # Will be retrieved on first request

def get_bot_info():
    """Get bot information (to determine its user_id)"""
    global TELEGRAM_BOT_USERNAME
    if TELEGRAM_BOT_USERNAME is None:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                TELEGRAM_BOT_USERNAME = bot_info["result"]["username"]
                logging.info(f"Bot: @{TELEGRAM_BOT_USERNAME}")
        except Exception as e:
            logging.error(f"Error getting bot information: {e}")
    return TELEGRAM_BOT_USERNAME

def send_message(chat_id, text, reply_to_message_id=None, chat_type=None):
    payload = {"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id}
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Error sending message: {response.status_code} - {response.text}")
        else:
            logging.info(f"The response has been sent. chat_type={chat_type}, ID={chat_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making request to Telegram API: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"]
        message_id = message.get("message_id")
        text = message.get("text", "").strip()
        text_lower = text.lower()
        user_name = message["from"].get("first_name", "User")
        
        # Get bot information (for reply checking)
        get_bot_info()

        # Check if there is a reply_to_message
        reply_to_message = message.get("reply_to_message")
        context = None
        is_reply_to_bot = False
        
        if reply_to_message:
            # Check if reply is a response to bot's message
            replied_from = reply_to_message.get("from", {})
            if replied_from.get("is_bot") and replied_from.get("username") == TELEGRAM_BOT_USERNAME:
                is_reply_to_bot = True
                # Extract context from the message being replied to
                context = reply_to_message.get("text", "")
                logging.info(f"Reply to bot message detected. Context: {context[:50]}...")

        # Determine if the bot should respond
        should_respond = False
        question = text
        
        if chat_type == "private":
            # In private chat, respond to all messages
            should_respond = True
        elif is_reply_to_bot:
            # In group, respond if it's a reply to our message
            should_respond = True
        elif text_lower.startswith((f"{TRIGGER_WORD} ", f"{TRIGGER_WORD},")):
            # In group, respond only if there is a trigger word
            should_respond = True
            question = text_lower.replace(f"{TRIGGER_WORD} ", "", 1).replace(f"{TRIGGER_WORD},", "", 1).strip()
        
        if should_respond:
            response_text = handler.handle_message(question, user_name, context=context)
            send_message(chat_id, response_text, reply_to_message_id=message_id, chat_type=chat_type)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
