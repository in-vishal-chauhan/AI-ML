import requests
from config import Config
# from logger import get_logger

# logger = get_logger(__name__)

class GrokAPI:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def ask(self, system_prompt, user_input):
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        }
        try:
            res = requests.post(self.endpoint, headers=self.headers, json=payload)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"GroqAPI.ask() failed: {str(e)} | Payload: {payload}")
            raise
