import requests
from twilio.rest import Client
from config import Config
from logger import get_logger
import threading
from services.database_service import Database
import json
from services.email_service import EmailService

logger = get_logger(__name__)
emailService = EmailService()

client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(from_number, to_number, body, retry_count=0, max_retries=3, delay=60, payload=None):
    try:
        msg = client.messages.create(body=body, from_=to_number, to=from_number, force_delivery=True)
        
        # Send confirmation email
        subject = "WhatsApp Message Sent Successfully"
        email_body = f"Message SID: {msg.sid}\nMessage Body: {body}"
        emailService.send_email(
            to_addr=emailService.to_addr,
            subject=subject,
            body=email_body
        )

        return msg.sid
    except Exception as e:
        attempt_number = retry_count + 1
        logger.error(f"Twilio message failed (attempt {attempt_number}): {str(e)}")

        if attempt_number < max_retries:
            threading.Timer(delay, send_whatsapp_message, args=(from_number, to_number, body, retry_count + 1, max_retries, delay)).start()
        else:
            logger.error("Max retries reached. Saving message data into database for further processing.")
            insert_query = "INSERT INTO whatsapp_messages (from_number, to_number, body, full_payload) VALUES (%s, %s, %s, %s)"
            database = Database()
            try:
                database.cursor.execute(insert_query, (from_number, to_number, body, json.dumps(payload)))
                database.conn.commit()

                subject = "WhatsApp Message Delivery Error"
                email_body = (
                    f"An error occurred while sending a WhatsApp message.\n\n"
                    f"Details:\n"
                    f"From: {from_number}\n"
                    f"To: {to_number}\n"
                    f"Message Body:\n{body}\n\n"
                    f"Payload:\n{json.dumps(payload, indent=2)}"
                )
                emailService.send_email(
                    to_addr=emailService.to_addr,
                    subject=subject,
                    body=email_body
                )

                logger.error(f"Failed to send WhatsApp message. Data inserted into database as a fallback.")
            except Exception as e:
                logger.error(f"Failed to save fallback data into database after WhatsApp message failure. Error: {str(e)}")
            finally:
                database.close()
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
