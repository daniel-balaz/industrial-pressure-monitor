import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramAlert:
    @staticmethod
    def send_alert(machine_id, hall, msg):
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id or not msg:
            return

        full_msg = f"STROJ: {machine_id} (Hala: {hall})\n{msg}"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        try:
            requests.post(url, data={"chat_id": chat_id, "text": full_msg}, timeout=5)
        except Exception as e:
            print(f"Chyba při odesílání na Telegram: {e}")