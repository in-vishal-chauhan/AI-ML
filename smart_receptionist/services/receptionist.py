import json
from logger import get_logger
from datetime import datetime
import requests
from tabulate import tabulate

logger = get_logger(__name__)

class AIReceptionist:
    def __init__(self, groq_api, db, document_qa_service):
        self.document_qa_service = document_qa_service
        self.groq_api = groq_api
        self.db = db

    def translate_to_english(self, text):
        system_prompt = """
        You are a translator. Your task is to translate the given text into English.
        Translate the text and return it in English.
        If the text is already in English, return it as is. strip it and return. 
        without any explanation. same as the input text.
        if the text is not in English, return it in English.
        follow my instructions strictly.
        just focus on your task do not add any extra information or explanation.
        """
        return self.groq_api.ask(system_prompt, text)

    def extract_parameters(self, english_text):
        system_prompt = """
        Persona:
        You are a precise field extractor that only returns structured JSON data.

        Task:
        From the given input text, extract the values for the following fields:
        - color
        - material
        - quality

        Constraints:
        - Always include all three fields in the output.
        - If any value is missing or not found, set its value as an empty string "".
        - Do not include any extra text, comments, or explanations.
        - Output must be valid JSON that can be parsed using json.loads.

        Output Format Example:
        {
        "color": "",
        "material": "",
        "quality": ""
        }
        """
        try:
            response = self.groq_api.ask(system_prompt, english_text).strip()
            logger.info(f"Extracted parameters: {response}")
            parsed = json.loads(response)
            filtered = {k: v for k, v in parsed.items() if v.strip()}
            return filtered
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e} | Raw response: {response}")
            return {}
    
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

            color = params.get("color", "")
            material = params.get("material", "")
            quality = params.get("quality", "")

            if not (color or material or quality):
                return "Please provide at least one of: color, material, or quality."

            results = self.db.get_rate(color, material, quality)

            if not results:
                return "No matching records found."

            table_data = [
                [r['color'], r['material'], r['quality'], f"{float(r['rate']):.2f}"]
                for r in results
            ]
            headers = ["Color", "Material", "Quality", "Rate"]

            table = tabulate(
                table_data,
                headers=headers,
                tablefmt="fancy_grid",
                colalign=("left", "left", "left", "right")
            )

            return f"```\nHere are the matching rates:\n{table}\nTotal: {len(results)}\n```"

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
