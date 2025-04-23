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
    system_message="Extract these attributes from the message: "
                   "color (e.g., red, blue, green, black, white), "
                   "material (e.g., cotton, silk, polyester), "
                   "quality (e.g., prime, premium, standard, high). "
                   "Return a JSON object with only found attributes as key-value pairs (e.g., {\"color\": \"red\", \"material\": \"cotton\"}). "
                   "Omit unfound attributes. Return {} if no attributes are found. "
                   "Ignore words like 'shirt', 'tshirt', 'price', 'give', 'want'. "
                   "Output only a valid JSON string, with no extra text, markup, or whitespace.",
    human_input_mode="NEVER"
)

user_input = input("Please enter a message: ")

response = outputAgent.generate_reply(
    messages=[{"content": user_input, "role": "user"}],
    sender=inputAgent
)

print(response)