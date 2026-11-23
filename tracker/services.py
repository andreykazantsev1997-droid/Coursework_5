import os
import requests


def send_telegram_message(chat_id: str, text: str) -> None:
    token = os.getenv("TG") or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()