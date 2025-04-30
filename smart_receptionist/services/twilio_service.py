import requests
from twilio.rest import Client
from config import Config
from logger import get_logger

logger = get_logger(__name__)

client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(from_number, to_number, body):
    try:
        msg = client.messages.create(body=body, from_=to_number, to=from_number)
        return msg.sid
    except Exception as e:
        logger.error(f"Twilio message failed: {str(e)}")
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
