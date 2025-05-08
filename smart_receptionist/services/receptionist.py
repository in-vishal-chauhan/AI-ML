import json
from logger import get_logger
from datetime import datetime
import requests
from tabulate import tabulate
from services.pinecone_service import PineconeService
from config import Config

logger = get_logger(__name__)

class AIReceptionist:
    def __init__(self, groq_api, db, read_store_vector):
        self.read_store_vector = read_store_vector
        self.groq_api = groq_api
        self.db = db

    def translate_to_english(self, text):
        system_prompt = """
        You are a professional translator.
        Your task is to translate any given input text into English.

        If the text is already in English, return it exactly as it is, with leading and trailing whitespace removed.
        If the text is not in English, translate it into proper English.
        Do not add any explanations, comments, or additional information.
        Do not mention that you are a translator or AI.
        Return only the translated or original English text—nothing else.

        Examples:
        Input: ¿Cómo estás?
        Output: How are you?

        Input: what is your name?
        Output: what is your name?

        Input: Je m'appelle Pierre.
        Output: My name is Pierre.

        Input: हेलो, आप कैसे हैं?
        Output: Hello, how are you?
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

            API_KEY = Config.PINECONE_API_KEY
            INDEX_NAME = "knowledge"
            NAMESPACE = "knowledge"

            service = PineconeService(api_key=API_KEY, index_name=INDEX_NAME, namespace=NAMESPACE)
            service.init_index()

            if not service.pc.has_index(INDEX_NAME):
                try:
                    records = self.read_store_vector.query()
                    service.upsert_documents(records)
                except Exception as e:
                    logger.error(f"Error during vector store upsertion: {str(e)}")
                    return "Sorry, we couldn't load the knowledge base right now. Please try again later."

            try:
                response = service.search(translated, top_k=10)
                return self.query_llm_with_chunks(response, self.groq_api, user_input)
            except Exception as e:
                logger.error(f"Error during Pinecone search: {str(e)}")
                return "Sorry, there was an issue while searching for your answer. Please try again."

        except Exception as e:
            logger.error(f"Error in check_in_document: {str(e)}")
            return "Apologies, something went wrong while processing your request. Please try again shortly."


    def query_llm_with_chunks(self, response, groq_api, user_input):
        try:
            all_chunks = [hit["fields"]["chunk_text"] for hit in response["result"]["hits"]]
            combined_context = "\n\n".join(all_chunks)

            prompt = f"""
            Use the following context to answer the question.

            If you found a proper answer, respond politely and clearly.
            If the answer cannot be found, respond politely that we currently do not have enough information.

            --- Context ---
            {combined_context}
            ----------------

            Question: {user_input}
            """

            return groq_api.ask(prompt.strip(), user_input)

        except Exception as e:
            logger.error(f"Error in query_llm_with_chunks: {str(e)}")
            return "Sorry, we couldn't generate a response at the moment. Please try again shortly."