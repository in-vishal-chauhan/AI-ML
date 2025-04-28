import requests
import json
import pymysql
from dotenv import load_dotenv
import os
import re
from flask import Flask, request, jsonify

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

def send_whatsapp_message(to_number, message_body):
    whatsapp_api_url = os.getenv("WHATSAPP_API_URL")
    whatsapp_api_token = os.getenv("WHATSAPP_API_TOKEN")

    headers = {
        "Authorization": f"Bearer {whatsapp_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }
    response = requests.post(whatsapp_api_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.json
    print(data)
    import pdb; pdb.set_trace()
    try:
        user_query = data["messages"][0]["text"]["body"]
        user_number = data["messages"][0]["from"]

    except (KeyError, IndexError):
        return jsonify({"error": "Invalid payload"}), 400

    response_text = receptionist.handle_query(user_query)

    try:
        send_result = send_whatsapp_message(user_number, response_text)
        print(f"Sent message: {response_text}")
        return jsonify({"status": "success", "details": send_result}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send WhatsApp message: {str(e)}"}), 500

@app.route("/")
def homepage():
    return """
    <html>
    <head><title>AI Receptionist</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
        <h1>🤖 AI Receptionist is Running!</h1>
        <p>Webhook Endpoint: <b>/webhook</b></p>
        <p>Send a message on WhatsApp to see it in action.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(port=5000)
