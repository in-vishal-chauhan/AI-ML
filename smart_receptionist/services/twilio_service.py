import requests
from twilio.rest import Client
from config import Config
from logger import get_logger
import threading

logger = get_logger(__name__)

client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(from_number, to_number, body, retry_count=0, max_retries=3, delay=300):
    try:
        msg = client.messages.create(body=body, from_=to_number, to=from_number)
        logger.info(f"WhatsApp message sent successfully: {msg.sid}")
        return msg.sid
    except Exception as e:
        attempt_number = retry_count + 1
        logger.error(f"Twilio message failed (attempt {attempt_number}): {str(e)}")
        
        if attempt_number < max_retries:
            threading.Timer(delay, send_whatsapp_message, args=(from_number, to_number, body, retry_count + 1, max_retries, delay)).start()
        else:
            logger.error("Max retries reached. Giving up.")
            '''
            In this case we store in db and then revert back when limit is restored
            '''
        return None

def download_audio(media_url, save_path):
    try:
        res = requests.get(media_url, auth=(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN))
        if res.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(res.content)
            return True
        else:
            logger.error(f"Download failed: {res.status_code}")
            return False
    except Exception as e:
        logger.error(f"Download exception: {str(e)}")
        return False
