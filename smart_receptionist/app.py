from flask import Flask, request, jsonify, render_template
import os

from services.twilio_service import download_audio, send_whatsapp_message
from services.whisper_service import transcribe_audio
from services.groq_service import GroqAPI
# from services.database_service import Database
from services.sqlite_db import SqliteDatabase
from services.receptionist import AIReceptionist
# from services.document_qa_service import DocumentQAService
from services.read_store_vector import ReadStoreVector
from logger import get_logger

app = Flask(__name__)
logger = get_logger(__name__)

# Initialize services
groq = GroqAPI()
db = SqliteDatabase()
# document_qa_service = DocumentQAService()
read_store_vector = ReadStoreVector()
receptionist = AIReceptionist(groq, db, read_store_vector)

@app.route("/webhook", methods=["POST"])
def webhook():
    audio_path = "./temp/temp_audio.ogg"
    try:
        data = request.form.to_dict() or request.get_json()
        msg_type = data.get("MessageType", "").lower()
        from_number = data.get("From", "")
        to_number = data.get("To", "")
        media_type = data.get("MediaContentType0", "")
        user_query = ""

        # Handle audio messages
        if msg_type == "audio" or (msg_type == "document" and media_type.startswith("audio/")):
            media_url = data.get("MediaUrl0")
            if download_audio(media_url, audio_path):
                user_query, language = transcribe_audio(audio_path)
                os.remove(audio_path)
            else:
                logger.error(f"Failed to download audio from URL: {media_url}")
                return jsonify({"error": "Failed to download audio"}), 502
        else:
            # Handle text messages
            user_query = data.get("Body", "")

        if not user_query:
            logger.error("Empty input received.")
            return jsonify({"error": "Empty input received"}), 400

        # Process query with receptionist agent
        response = receptionist.orchestrator(user_query)

        # Send response back to user via WhatsApp
        if send_whatsapp_message(from_number, to_number, response, payload=data):
            return jsonify({"message": "Sent!"}), 200
        else:
            logger.error(f"Failed to send WhatsApp message via Twilio. From: {from_number}, To: {to_number}, Payload: {data}")
            return jsonify({"error": "Failed to send WhatsApp message"}), 502

    except Exception as e:
        logger.exception(f"Unhandled exception during webhook processing: {str(e)}")
        return jsonify({"error": "Unhandled exception during webhook processing"}), 500

@app.route("/")
def index():
    return "<h1>AI Receptionist is running</h1>"

@app.route("/logs")
def show_logs():
    log_path = 'webhook.log'
    if not os.path.exists(log_path):
        return "<h3>Log file not found.</h3>", 404

    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    # HTML structure with styles for proper word wrapping and formatting
    html = f"""
    <html>
    <head>
        <style>
            body {{
                background: #f4f4f4;
                color: #333;
                font-family: 'Courier New', monospace;
                padding: 20px;
                margin: 0;
            }}
            h2 {{
                color: #4CAF50;
            }}
            pre {{
                background: #1e1e1e;
                color: #f5f5f5;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #444;
                white-space: pre-wrap;       /* Wrap long lines */
                word-wrap: break-word;      /* Break long words */
                max-width: 100%;
                overflow-x: auto;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <h2>📄 Application Logs</h2>
        <pre>{content}</pre>
    </body>
    </html>
    """
    return html

@app.route('/chat')
def chat():
    return render_template("chat.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
