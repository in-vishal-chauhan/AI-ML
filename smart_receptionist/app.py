from flask import Flask, request, jsonify
import os

from services.twilio_service import download_audio, send_whatsapp_message
from services.whisper_service import transcribe_audio
from services.groq_service import GroqAPI
from services.database_service import Database
from services.receptionist import AIReceptionist
from logger import get_logger
from services.document_qa_service import DocumentQAService

app = Flask(__name__)
logger = get_logger(__name__)

groq = GroqAPI()
db = Database()
document_qa_service = DocumentQAService()
receptionist = AIReceptionist(groq, db, document_qa_service)

@app.route("/webhook", methods=["POST"])
def webhook():
    audio_path = "./temp/temp_audio.ogg"
    try:
        data = request.form.to_dict() or request.get_json()
        msg_type = data.get("MessageType", "").lower()
        user_query = ""
        from_number = data.get("From", "")
        to_number = data.get("To", "")
        media_type = data.get("MediaContentType0", "")

        if msg_type == "audio" or (msg_type == "document" and media_type.startswith("audio/")):
            media_url = data.get("MediaUrl0")
            if download_audio(media_url, audio_path):
                user_query, _ = transcribe_audio(audio_path)
                os.remove(audio_path)
            else:
                return jsonify({"error": "Failed to download audio"}), 500
        else:
            user_query = data.get("Body", "")

        if not user_query:
            return jsonify({"error": "Empty input"}), 400

        response = receptionist.orchestrator(user_query)
        if send_whatsapp_message(from_number, to_number, response, payload=data):
            return jsonify({"message": "Sent!"}), 200
        else:
            return jsonify({"error": "Twilio failed"}), 500

    except Exception as e:
        logger.exception("Webhook error:")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "<h1>AI Receptionist is running</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
