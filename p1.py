import openai
import os

# Set your API key
openai.api_key = "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"# or hardcode your key directly (not recommended)

# Get user input
user_input = input("Ask something: ")

# Call the ChatGPT API
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # or "gpt-4" if available
    messages=[
        {"role": "user", "content": user_input}
    ]
)

# Show the response
answer = response['choices'][0]['message']['content']
print("AI says:", answer)
