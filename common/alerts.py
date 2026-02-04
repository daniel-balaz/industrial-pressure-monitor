# IMPORT
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class TelegramAlert:
    @staticmethod
    def send_alert(machine_id, hall, msg):
        # LOADING CREDENTIALS FROM .env FOR SECURITY
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # CHECK IF ALL NECESSARY DATA IS PRESENT BEFORE SENDING
        if not token or not chat_id or not msg:
            return

        # FORMATING THE LAST MESSAGE FOR BETTER READABILITY
        full_msg = f"STROJ: {machine_id} (Hala: {hall})\n{msg}"
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        try:
            requests.post(url, data={"chat_id": chat_id, "text": full_msg}, timeout=5)
        except Exception as e:
            logging.error(f"Chyba při odesílání na Telegram: {e}")