from autogen import ConversableAgent

llm_config = {
    "model": "llama-3.2-1b",
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
    system_message="Your name is Jemaine and you are a stand-up comedian in a two-person comedy show.",
)
print("Program started...")
chat_result = bret.generate_reply(
    sender = jemaine,
    message="Tell me a joke",
)
print("Program end...")

print(len(chat_result))
# print(chat_result.last_message()["content"])
# for msg in chat_result.chat_history:
#     print(msg.get("content", ""))
    # chat result reply on whatsapp number