import json
from logger import get_logger

logger = get_logger(__name__)

class AIReceptionist:
    def __init__(self, groq_api, db):
        self.groq_api = groq_api
        self.db = db

    def translate_to_english(self, text):
        system_prompt = """
        You are a strict translator. 
        ONLY translate non-English parts to English without guessing, adding, changing or improving words.
        If the original text is already English, return it exactly as is.
        DO NOT interpret, summarize, or rephrase. 
        Just do literal translation, word by word.
        """
        return self.groq_api.ask(system_prompt, text)

    def extract_parameters(self, english_text):
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

            required_fields = ['color', 'material', 'quality']
            extracted_fields = {field: params.get(field) for field in required_fields if params.get(field)}
            missing_fields = [field for field in required_fields if not params.get(field)]
            if missing_fields:
                missing_list = ', '.join(missing_fields)
                extracted_list = ', '.join(f"{k}: {v}" for k, v in extracted_fields.items())
                return f"Sorry, the following details are missing: {missing_list}. Extracted values: {extracted_list or 'None'}. Please provide the missing information to get the rate."
            if rate:
                return f"The rate for {params['color']}, {params['material']}, {params['quality']} is ₹{rate}."
            return f"Sorry, we couldn't find the rate for {params['color']}, {params['material']}, {params['quality']}."

        except Exception as e:
            logger.error(f"handle_query failed: {str(e)}")
            return "An error occurred while processing your request."
