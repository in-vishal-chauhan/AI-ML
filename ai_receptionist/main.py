import requests
import json
import pymysql
from dotenv import load_dotenv
import os
import re
from flask import Flask, request, jsonify
from twilio.rest import Client
from faster_whisper import WhisperModel
model = WhisperModel("base", compute_type="float32")
import logging

logging.basicConfig(
    filename="webhook.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - Line %(lineno)d - %(message)s"
)
load_dotenv()
app = Flask(__name__)

class GroqAPI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def ask(self, system_prompt, user_input):
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        }
        response = requests.post(self.endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.conn.cursor()

    def get_rate(self, color, material, quality):
        color = re.sub(r'[^a-zA-Z0-9]', '', color.lower())
        material = re.sub(r'[^a-zA-Z0-9]', '', material.lower())
        quality = re.sub(r'[^a-zA-Z0-9]', '', quality.lower())
        query = """
        SELECT rate FROM products
        WHERE 
            LOWER(REPLACE(REPLACE(REPLACE(color, ' ', ''), '-', ''), '_', '')) = %s
            AND LOWER(REPLACE(REPLACE(REPLACE(material, ' ', ''), '-', ''), '_', '')) = %s
            AND LOWER(REPLACE(REPLACE(REPLACE(quality, ' ', ''), '-', ''), '_', '')) = %s
        """
        self.cursor.execute(query, (color, material, quality))
        result = self.cursor.fetchone()
        return result["rate"] if result else None

    def close(self):
        self.cursor.close()
        self.conn.close()

class AIReceptionist:
    def __init__(self, groq_api: GroqAPI, database: Database):
        self.groq_api = groq_api
        self.database = database

    def translate_to_english(self, user_query):
        system_prompt = """
        You are a strict translator. 
        ONLY translate non-English parts to English without guessing, adding, changing or improving words.
        If the original text is already English, return it exactly as is.
        DO NOT interpret, summarize, or rephrase. 
        Just do literal translation, word by word.
        """
        return self.groq_api.ask(system_prompt, user_query)

    def extract_parameters(self, english_query):
        system_prompt = """
        You are an extractor. From the text, extract three things:
        - color
        - material
        - quality

        Return ONLY a JSON like this:
        {
            "color": "",
            "material": "",
            "quality": ""
        }
        """
        extracted = self.groq_api.ask(system_prompt, english_query)
        return json.loads(extracted)

    def format_response(self, color, material, quality, rate):
        if rate:
            return f"The rate for {color}, {material}, {quality} is ₹{rate}."
        else:
            return (
                f"Sorry, we couldn't find the rate for {color}, {material}, {quality}."
            )

    def handle_query(self, user_query):
        try:
            english_query = self.translate_to_english(user_query)
            params = self.extract_parameters(english_query)
            color = params.get("color")
            material = params.get("material")
            quality = params.get("quality")

            rate = self.database.get_rate(color, material, quality)
            return self.format_response(color, material, quality, rate)

        except Exception as e:
            return f"An error occurred: {str(e)}"

groq = GroqAPI()
db = Database()
receptionist = AIReceptionist(groq, db)

def send_whatsapp_message(from_number, to_number, response_text):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=response_text,
            from_=to_number,
            to=from_number,
        )
        return message.sid
    except Exception as e:
        logging.error(f"Failed to send message: {str(e)}")
        return None

def download_audio(media_url, save_path):
    """Downloads audio file from Twilio Media URL."""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    response = requests.get(media_url, auth=(account_sid, auth_token))
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    return False

def transcribe_audio(file_path):
    """Transcribes audio using faster-whisper."""
    segments, info = model.transcribe(file_path, beam_size=5, language="en")
    transcript = " ".join(segment.text for segment in segments)
    return transcript, info.language

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    audio_path = "./temp_audio.ogg"
    try:
        # Support both form and JSON (for flexibility)
        data = request.form.to_dict() or request.get_json() or {}

        message_type = data.get("MessageType", "").lower()
        from_number = data.get("From", "")
        to_number = data.get("To", "")
        user_query = ""

        if message_type == "audio":
            media_url = data.get("MediaUrl0", "")
            if not media_url:
                logging.error("No media URL found in request.")
                return jsonify({"error": "No media URL found."}), 400

            if not download_audio(media_url, audio_path):
                logging.error("Failed to download audio from URL.")
                return jsonify({"error": "Failed to download audio."}), 500

            try:
                user_query, detected_language = transcribe_audio(audio_path)
                logging.info(f"Transcribed query: {user_query} | Language: {detected_language}")
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)

        else:
            user_query = data.get("Body", "")
            logging.info(f"Received text query: {user_query}")

        if not user_query:
            logging.warning("Empty user query received.")
            return jsonify({"error": "Empty query."}), 400

        response_text = receptionist.handle_query(user_query)
        logging.info(f"Response generated: {response_text}")

        if send_whatsapp_message(from_number, to_number, response_text):
            return jsonify({"message": "Message sent successfully!"}), 200
        else:
            logging.error("Failed to send message back to user.")
            return jsonify({"error": "Unable to process your request right now. Please try again later."}), 500

    except Exception as general_error:
        logging.exception("Unhandled exception occurred:")
        return jsonify({"error": f"Error in webhook handling: {str(general_error)}"}), 500

@app.route("/")
def homepage():
    return """
    <html>
    <head><title>AI Receptionist</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
        <h1>🤖 AI Receptionist is Running!</h1>
        <p>Send a message on WhatsApp to see it in action.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(port=5000,debug=True)
