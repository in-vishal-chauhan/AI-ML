from autogen import ConversableAgent

llm_config = {
    "model": "llama-3.2-1b",
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

user_input = input("Enter your question or instruction: ")

chat_result = bret.initiate_chat(
    recipient=jemaine,
    message=user_input,
    max_turns=1
)

print(chat_result.summary)