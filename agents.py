import autogen

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "temperature": 0,
    "price": [0, 0]
}

inputAgent = autogen.ConversableAgent(
    name="InputAgent",
    llm_config=llm_config,
    system_message="You are the user providing input messages.",
    human_input_mode="NEVER"
)

outputAgent = autogen.ConversableAgent(
    name="OutputAgent",
    llm_config=llm_config,
    system_message="Extract only valid color names (e.g., red, blue, black, green) from the received message. Do not include non-color words like 'cotton' or other descriptors. Respond with only the color names, one per line, with no additional text, explanation, or whitespace. If no valid colors are found, respond with 'None'.",
    human_input_mode="NEVER"
)

user_input = input("Please enter a message: ")

response = outputAgent.generate_reply(
    messages=[{"content": user_input, "role": "user"}],
    sender=inputAgent
)

print(response)