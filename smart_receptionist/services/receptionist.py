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
        try:
            return self.groq_api.ask(system_prompt, text)
        except Exception as e:
            logger.error(f"Translation failed for text: {text}\nError: {str(e)}")
            raise

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
            parsed = json.loads(response)
            filtered = {k: v for k, v in parsed.items() if v.strip()}
            return filtered
        except Exception as e:
            logger.exception(f"Error occurred inside extract_parameters function: {str(e)}")
            raise
    
    def orchestrator(self, user_input):
        system_prompt = """
        You are an orchestrator.

        Your task is to decide whether the user's input is:
        - A generic query (e.g., greetings or general questions), or
        - A rate-related query (e.g., asking for prices or rates).

        Based on your decision, return ONLY one of these function names:
        - check_in_document
        - check_in_db

        Do not explain. Just return the exact function name.
        """

        try:
            function_name = self.groq_api.ask(system_prompt, user_input).strip()
            return getattr(self, function_name)(user_input)
        except Exception as e:
            logger.exception(f"Error occurred inside orchestrator function: {str(e)}")
            raise

    def check_in_db(self, user_input):
        try:
            translated = self.translate_to_english(user_input)
            params = self.extract_parameters(translated)

            color = params.get("color")
            material = params.get("material")
            quality = params.get("quality")

            if not (color or material or quality):
                return "To help you better, please share at least one detail such as color, material, or quality."

            results = self.db.get_rate(color, material, quality)

            if not results:
                return "Sorry, I couldn't find any matching records. Please try refining your search."

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

            return f"```\nGreat! Here are the rates I found for you:\n\n{table}\n\nTotal matches: {len(results)}\n```"

        except Exception as e:
            logger.error(f"Error occurred inside check_in_db function: {str(e)}")
            return "Apologies, something went wrong while processing your request. We're looking into it — please try again shortly."


    def check_in_document(self, user_input):
        try:
            translated = self.translate_to_english(user_input)
            return self.document_qa_service.query(translated, self.groq_api)
        except Exception as e:
            logger.error(f"Error occurred inside check_in_document function: {str(e)}")
            return "Apologies, something went wrong while processing your request. We're looking into it — please try again shortly."