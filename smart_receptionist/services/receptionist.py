import json
from logger import get_logger
from datetime import datetime
import requests

logger = get_logger(__name__)

class AIReceptionist:
    def __init__(self, groq_api, db, document_qa_service):
        self.document_qa_service = document_qa_service
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
    
    def orchestrator(self, user_input):
        system_prompt = """
        You are an orchestrator.

        Your task is to decide whether the user's input is:
        - A generic query (e.g., greetings or general questions), or
        - A rate-related query (e.g., asking for prices or rates).
        - Date-related query (current date, time, day)
        - Web query (needs external information from internet like capital cities, who is Elon Musk, weather, temperature, etc.)

        Based on your decision, return ONLY one of these function names:
        - handle_generic_query
        - handle_query
        - handle_date_query
        - handle_web_query

        Do not explain. Just return the exact function name.
        """

        function_name = self.groq_api.ask(system_prompt, user_input).strip()
        return getattr(self, function_name)(user_input)

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
    
    def handle_generic_query(self, user_input):
        try:
            translated = self.translate_to_english(user_input)
            return self.document_qa_service.query(translated, self.groq_api)
        except Exception as e:
            logger.error(f"handle_generic_query failed: {str(e)}")
            return "An error occurred while processing your request."
    
    def handle_date_query(self, user_input):
        try:
            now = datetime.now()
            formatted_date = now.strftime("%A, %d %B %Y")
            formatted_time = now.strftime("%I:%M %p")
            return (
                f"📅 Today is **{formatted_date}**.\n"
                f"⏰ The current time is **{formatted_time}**.\n"
                "Let me know if you need anything else!"
            )
        except Exception as e:
            logger.error(f"handle_date_query failed: {str(e)}")
            return "Oops! I couldn't fetch the current date and time. Please try again shortly."

    def handle_web_query(self, user_input):
        try:
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": user_input,
                    "format": "json",
                    "no_redirect": 1,
                    "no_html": 1
                }
            )
            data = response.json()
            logger.info(f"Web query response: {data}")
            answer = data.get("Abstract") or data.get("Answer") or data.get("Definition")

            if answer:
                return f"🔍 Here's what I found:\n\n{answer}\n\nLet me know if you'd like to dig deeper!"
            else:
                return (
                    "Hmm... I couldn't find a direct answer to that 🤔.\n"
                    "You might want to try rephrasing your question or ask something else!"
                )

        except Exception as e:
            logger.error(f"handle_web_query failed: {str(e)}")
            return "Sorry! I ran into an issue while looking that up. Please try again soon."
