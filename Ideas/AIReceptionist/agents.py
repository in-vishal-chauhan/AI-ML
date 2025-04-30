# agents.py

import mysql.connector
import requests
import json

class ConversionAgent:
    """Handles voice-to-text conversion (placeholder for future)."""
    def __init__(self):
        pass

    def voice_to_text(self, voice_file_path):
        raise NotImplementedError("Voice-to-Text conversion not yet implemented.")


class TranslateAndFormatterAgent:
    """Handles translation, extraction, database query, and formatting."""

    def __init__(self, db_config, groq_api_key):
        self.db_config = db_config
        self.groq_api_key = groq_api_key

    def ask_groq(self, incoming_text):
        """Use Groq model to translate and extract structured data."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
You are an AI assistant helping to process customer queries for products. 
Each product has three attributes: Color, Material, and Quality.

Your job:
- Translate the input to English if needed.
- Extract 'color', 'material', and 'quality' from the text.
- If any of them is missing, reply with JSON {{"color": null, "material": null, "quality": null}}.
- Only return pure JSON output without any explanation.

Input: \"\"\"{incoming_text}\"\"\"
        """

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            try:
                content = response.json()["choices"][0]["message"]["content"]
                return json.loads(content)
            except Exception as e:
                print(f"Error parsing Groq response: {e}")
                return None
        else:
            print(f"Groq API error: {response.status_code} {response.text}")
            return None

    def query_database(self, attributes):
        """Query MySQL database for the product rate."""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT price FROM products
                WHERE color = %s AND material = %s AND quality = %s
            """
            values = (attributes['color'], attributes['material'], attributes['quality'])
            cursor.execute(query, values)
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result['price'] if result else None
        except Exception as e:
            print(f"Database query error: {e}")
            return None

    def process_message(self, incoming_text):
        """Full flow: Translate, extract, query DB, return response."""
        extracted = self.ask_groq(incoming_text)

        if not extracted or not (extracted.get('color') and extracted.get('material') and extracted.get('quality')):
            return "Sorry, I could not understand your request clearly. Please mention color, material, and quality."

        price = self.query_database(extracted)

        if price is None:
            return f"Sorry, the product '{extracted['color']} {extracted['material']} {extracted['quality']}' is not available right now."

        return f"The price for {extracted['color']} {extracted['material']} {extracted['quality']} is {price} INR."
