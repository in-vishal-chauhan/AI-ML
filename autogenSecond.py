from autogen import ConversableAgent

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://localhost:1234/v1",
    "api_key": "lm-studio",
    "price": [0,0],
}

bret = ConversableAgent(
    name="Bret",
    llm_config=llm_config,
    system_message="Your name is Bret and you are a stand-up comedian in a two-person comedy show.",
)

jemaine = ConversableAgent(
    name="Jemaine",
    llm_config=llm_config,
    system_message="Your name is Jemain and you are a stand-up comedian in a two-person comedy show.",
)

chat_result = bret.initiate_chat(
    recipient = jemaine,
    message="Jemaine, tell me a joke.", 
)

for msg in chat_result.chat_history:
    print(msg.get("content", ""))