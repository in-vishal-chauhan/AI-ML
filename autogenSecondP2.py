from autogen import ConversableAgent

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "price": [0,0]
}

bret = ConversableAgent(
    name="Bret",
    llm_config=llm_config,
    system_message="Your name is Bret and you are a stand-up comedian in a two-person comedy show.",
)

jemaine = ConversableAgent(
    name="Jemaine",
    llm_config=llm_config,
    system_message="Your name is Jemaine and you are a stand-up comedian in a two-person comedy show.",
)

chat_result = bret.generate_reply(
    sender = jemaine,
    messages=[{"role": "user", "content": "Tell me a joke"}]
)

print(chat_result)