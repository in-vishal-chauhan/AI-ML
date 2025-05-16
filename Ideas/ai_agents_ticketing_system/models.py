from openai import OpenAI
import os
from autogen import ConversableAgent, AssistantAgent, GroupChat, GroupChatManager
import json

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


# llm_config = {
#     "model": "llama-3.2-1b",
#     "base_url": "http://127.0.0.1:1234/v1/chat/completions",
#     "api_key": "lm-studio",
#     "price": [0,0]
# }
# def get_llama_response(prompt: str) -> str:
#     agent = ConversableAgent(
#         name="SmartAssistant",
#         llm_config=llm_config,
#         human_input_mode="NEVER",
#     )

#     response = agent.generate_reply(
#         messages=[{"content": prompt, "role": "user"}]
#     )

#     print("Chatbot says:", response)

#     return response