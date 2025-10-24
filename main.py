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
    """Загрузка файла из Google Cloud Storage"""
    try:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        content = blob.download_as_text(encoding="utf-8")
        return json.loads(content)
    except Exception as e:
        logging.error(f"Ошибка при загрузке конфига из GCS: {e}")
        raise

# Определяем, где запущен скрипт и загружаем конфигурацию
is_cloud_run = os.environ.get("K_SERVICE") is not None

if is_cloud_run:
    BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    if not BUCKET_NAME:
        raise ValueError("GCS_BUCKET_NAME не задан в переменных окружения")
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
            raise ValueError("GCS_BUCKET_NAME не задан в переменных окружения")
        config = load_from_gcs(BUCKET_NAME, "config.json")

handler = MessageHandler(config)

TRIGGER_WORD = config.get("trigger_word")
if not TRIGGER_WORD:
    raise ValueError("trigger_word не задан в конфигурации")
TRIGGER_WORD = TRIGGER_WORD.lower()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не задан! Убедитесь, что он установлен в переменных окружения.")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_message(chat_id, text, reply_to_message_id=None):
    payload = {"chat_id": chat_id, "text": text, "reply_to_message_id": reply_to_message_id}
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        if response.status_code != 200:
            logging.error(f"Ошибка отправки сообщения: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к Telegram API: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"]
        message_id = message.get("message_id")
        text = message.get("text", "").strip().lower()
        user_name = message["from"].get("first_name", "Пользователь")

        # В приватных чатах отвечаем на все сообщения
        # В группах требуем триггерное слово
        should_respond = False
        question = text
        
        if chat_type == "private":
            # В приватном чате отвечаем на все сообщения
            should_respond = True
        elif text.startswith((f"{TRIGGER_WORD} ", f"{TRIGGER_WORD},")):
            # В группе отвечаем только если есть триггерное слово
            should_respond = True
            question = text.replace(f"{TRIGGER_WORD} ", "", 1).replace(f"{TRIGGER_WORD},", "", 1).strip()
        
        if should_respond:
            response_text = handler.handle_message(question, user_name)
            send_message(chat_id, response_text, reply_to_message_id=message_id)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
