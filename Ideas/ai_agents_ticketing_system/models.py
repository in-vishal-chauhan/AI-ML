from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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"
)

def get_llama_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()