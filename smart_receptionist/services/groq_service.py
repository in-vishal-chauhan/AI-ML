import requests
from config import Config
from logger import get_logger

logger = get_logger(__name__)

class GroqAPI:
    def __init__(self):
        self.llm_api_key = Config.LLM_API_KEY
        self.llm_endpoint = Config.LLM_ENDPOINT
        self.headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json",
        }

    def ask(self, system_prompt, user_input):
        payload = {
            "model": Config.LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        }
        try:
            res = requests.post(self.llm_endpoint, headers=self.headers, json=payload)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Unexpected error in GroqAPI.ask(): {e} | Payload: {payload}")
            raise
