import json
from logger import get_logger

logger = get_logger(__name__)

class AIReceptionist:
    def __init__(self, groq_api, db):
        self.groq_api = groq_api
        self.db = db

    def translate_to_english(self, text):
        system_prompt = """
        You are a strict translator...
        """
        return self.groq_api.ask(system_prompt, text)

    def extract_parameters(self, english_text):
        system_prompt = """
        You are an extractor...
        """
        return json.loads(self.groq_api.ask(system_prompt, english_text))

    def handle_query(self, user_input):
        try:
            translated = self.translate_to_english(user_input)
            params = self.extract_parameters(translated)
            rate = self.db.get_rate(
                params.get("color", ""),
                params.get("material", ""),
                params.get("quality", "")
            )
            if rate:
                return f"The rate for {params['color']}, {params['material']}, {params['quality']} is ₹{rate}."
            return f"Sorry, we couldn't find the rate for {params['color']}, {params['material']}, {params['quality']}."
        except Exception as e:
            logger.error(f"handle_query failed: {str(e)}")
            return "An error occurred while processing your request."
