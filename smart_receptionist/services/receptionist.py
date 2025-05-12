import json
from logger import get_logger
from tabulate import tabulate
from services.pinecone_service import PineconeService
from config import Config
from datetime import datetime

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
        carefully check all input text don't hallucinate the text just extract exact parameters.

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
        You are an AI orchestrator. Choose the best functions for the user's request.

        Functions:
        - check_in_document: For company or document-related questions.
        - check_in_db: For product prices, rates, or system data.
        - suggest_clothing_combination: For outfit or clothing suggestions.
        - get_current_date: To get the current date.
        - calculate_profit: For profit calculations.

        Reply with function names, comma-separated. Example: check_in_db, suggest_clothing_combination
        """.strip()

        tool_labels = {
            "check_in_document": "Company Info",
            "check_in_db": "Product Rates",
            "suggest_clothing_combination": "Clothing Suggestions",
            "get_current_date": "Current Date",
            "calculate_profit": "Profit Calculation",
        }

        try:
            tools_str = self.groq_api.ask(system_prompt, user_input)
            tools = [t.strip() for t in tools_str.split(",") if t.strip()]
            if not tools:
                return "We couldn’t find anything. Could you please rephrase or provide more details?"

            results = []
            context = user_input
            for key, tool in enumerate(tools):
                label = tool_labels.get(tool)
                if not label:
                    continue
                result = getattr(self, tool)(context)
                results.append(f"\n{label}:\n{result}")
                context += f"\n\n--- Result from {label} ---\n{result}\n"
            return "\n".join(results)

        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}")
            return "Something went wrong. Please try again."


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

            Use only the information provided in the context to answer the user's question. Do not add explanations, assumptions, or commentary. Do not mention whether something was found or not.

            Instructions:
            - If the answer exists in the context, return it directly and clearly.
            - If no answer is available, say nothing.
            - Do not say things like “There is no information” or “That is not available.”
            - Do not justify or explain your response.

            Your response should include only what is relevant and found in the context.

            --- Context ---
            {combined_context}
            ----------------

            Question: {user_input}

            based on this data just give available info dont say not found for this or this context
            """

            return groq_api.ask(prompt.strip(), user_input)

        except Exception as e:
            logger.error(f"Error in query_llm_with_chunks: {str(e)}")
            return "Sorry, we couldn't generate a response at the moment. Please try again shortly."


    def suggest_clothing_combination(self, user_input):
        system_prompt = """
        You’re a helpful fashion assistant.

        The user will tell you what they’re wearing or planning to wear. Suggest one color that would go well with their outfit, based on good fashion sense—like matching, contrast, or style harmony.

        Just reply with the color. No need to explain or mention any clothing items.

        Example: "Olive green"
        """

        try:
            suggestion = self.groq_api.ask(system_prompt, user_input).strip()
            return suggestion
        except Exception as e:
            logger.error(f"Error in suggest_clothing_combination: {str(e)}")
            return "Sorry, I couldn't come up with a suggestion right now."


    def get_current_date(self, user_input=None):
        return datetime.now().strftime("%A, %d %B %Y")
    
    def calculate_profit(self, user_input):
        system_prompt = """
        You are a smart profit calculator assistant.

        The user will provide:
        - A cost price (also referred to as "rate" or "base price")
        - A desired profit percentage (e.g., "I want 20% profit")

        Your job is to:
        1. Extract the cost price and profit percentage from the input.
        2. Calculate:
        - Profit = cost_price * (profit_percent / 100)
        - Selling Price = cost_price + profit
        3. Reply in plain text using this format:

        Cost Price = <cost_price>  
        Profit Percentage = <profit_percent>  
        Profit Amount = <profit_amount>  
        Selling Price = <selling_price>

        If cost price or profit percentage is missing, respond clearly asking the user to provide both values.
        if table have many values then calculate for each item
        """

        try:
            profitInfo = self.groq_api.ask(system_prompt, user_input).strip()
            return profitInfo
        except Exception as e:
            logger.error(f"Error in calculate_profit: {str(e)}")
            return "I couldn't calculate the profit. Please make sure to include both the cost price (e.g., 'rate is 100') and the profit percentage (e.g., 'want 20% profit') in your message."