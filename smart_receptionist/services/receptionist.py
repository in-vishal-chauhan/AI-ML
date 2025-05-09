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
        You are a precise field extractor that only returns structured JSON data.

        Your task is to extract values for the following fields from the input text:
        - color
        - material
        - quality

        Constraints:
        - Always include all three fields in the output.
        - If any value is missing or not found, set its value as an empty string "".
        - Do not include any extra text, comments, or explanations.
        - Output must be valid JSON that can be parsed using json.loads.

        Output format:
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

        Your task is to decide which of the following functions are most suitable for handling the user's query.

        Functions:
        - check_in_document: Use this when the user is asking about company-related information or details found in documents.
        - check_in_db: Use this when the user is asking about prices, rates, or any data stored in the system.
        - suggest_clothing_combination: Use this when the user wants suggestions for clothing colors, styles, or outfit combinations.

        Return a comma-separated list of function names in order of relevance.

        Do not explain your choices. Only output the function names like: check_in_db, suggest_clothing_combination
        """

        tool_labels = {
            "check_in_document": "Check for details about company",
            "check_in_db": "Find rate in our system",
            "suggest_clothing_combination": "Suggest a good clothing combination"
        }

        try:
            tools_str = self.groq_api.ask(system_prompt, user_input).strip()

            tools = []
            for t in tools_str.split(","):
                t = t.strip()
                if t:
                    tools.append(t)

            if not tools:
                return (
                    "Sorry, I couldn't find the best tool for your request. Could you please rephrase or provide more details?"
                )

            full_response = "Results:\n"

            for tool in tools:
                label = tool_labels.get(tool, None)

                if label is None:
                    full_response += f"\nSorry, I couldn't recognize the tool '{tool}'. Skipping it."
                    continue

                choice = input(f"\nWould you like me to run '{label}' and show the result? (yes/no): ").strip().lower()

                if choice == 'yes':
                    try:
                        result = getattr(self, tool)(user_input)
                        full_response += f"\n🔧 {label} Result:\n{result}"
                    except Exception as e:
                        full_response += f"\nThere was an error running the '{label}' tool: {str(e)}"
                elif choice == 'no':
                    full_response += f"\nSkipped: {label}"
                else:
                    full_response += "\nSorry, I didn't understand your response. Skipping this tool."

            return full_response.strip()

        except Exception as e:
            logger.exception("Error in orchestrator")
            return "Something went wrong while processing your request. Please try again."

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

            if not service.pc.has_index(INDEX_NAME):
                try:
                    service.init_index()
                    records = self.read_store_vector.query()
                    service.upsert_documents(records)
                    import time
                    time.sleep(10)
                    response = service.search(translated, top_k=10)
                    return self.query_llm_with_chunks(response, self.groq_api, user_input)
                except Exception as e:
                    logger.error(f"Error during vector store upsertion: {str(e)}")
                    return "Sorry, we couldn't load the knowledge base right now. Please try again later."

            try:
                service.init_index()
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
            You are a helpful assistant.

            Use the following context to answer the user's question.

            - If the answer is clearly found in the context, respond politely with the relevant information.
            - If the answer is not available, respond politely that the information is not currently in the knowledge base.
            - Optionally, suggest the user try rephrasing the question.

            --- Context ---
            {combined_context}
            ----------------

            Question: {user_input}
            """

            return groq_api.ask(prompt.strip(), user_input)

        except Exception as e:
            logger.error(f"Error in query_llm_with_chunks: {str(e)}")
            return "Sorry, we couldn't generate a response at the moment. Please try again shortly."


    def suggest_clothing_combination(self, user_input):
        """
        Uses the LLM to suggest a clothing color combination based on user's input.
        """
        system_prompt = """
        You are a fashion assistant.

        The user will describe what they are wearing or planning to wear.
        Your job is to suggest the most suitable color combination for the rest of the outfit,
        considering general fashion principles (contrast, complementarity, style harmony).

        Respond with only the suggested clothing item and color. Do not explain.
        Example format: "Navy blue pants", "White sneakers"
        """

        try:
            suggestion = self.groq_api.ask(system_prompt, user_input).strip()
            return suggestion
        except Exception as e:
            logger.error(f"Error in suggest_clothing_combination: {str(e)}")
            return "Sorry, I couldn't come up with a suggestion right now."