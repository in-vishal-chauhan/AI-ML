import autogen
import json

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
    system_message="Take the provided color, material, and quality values. "
                   "Return a JSON object with only non-empty attributes as key-value pairs (e.g., {\"color\": \"green\", \"material\": \"cotton\", \"quality\": \"prime\"}). "
                   "Omit empty or missing attributes. Return {} if no attributes are provided. "
                   "Output only a valid JSON string.",
    human_input_mode="NEVER"
)

color = input("Enter color: ").strip()
material = input("Enter material: ").strip()
quality = input("Enter quality: ").strip()

# Create a message with the inputs
input_message = f"color: {color}, material: {material}, quality: {quality}"

# Generate response from OutputAgent
response = outputAgent.generate_reply(
    messages=[{"content": input_message, "role": "user"}],
    sender=inputAgent
)

print(response)