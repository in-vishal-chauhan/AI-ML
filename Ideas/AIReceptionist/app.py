# app.py

from flask import Flask, request, jsonify
from agents import TranslateAndFormatterAgent

app = Flask(__name__)

# Database connection config
db_config = {
    'host': 'localhost',
    'user': 'your_db_user',
    'password': 'your_db_password',
    'database': 'your_database_name'
}

# Groq API Key
GROQ_API_KEY = "your_actual_groq_api_key"

# Initialize AI agent
ai_agent = TranslateAndFormatterAgent(db_config=db_config, groq_api_key=GROQ_API_KEY)

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    try:
        data = request.get_json()
        
        sender = data.get('from')
        incoming_text = data.get('message')

        if not incoming_text:
            return jsonify({"status": "error", "message": "No text received"}), 400

        reply_text = ai_agent.process_message(incoming_text)

        return jsonify({
            "status": "success",
            "reply_to": sender,
            "reply_message": reply_text
        })

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
