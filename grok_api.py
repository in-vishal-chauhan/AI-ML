import requests

API_KEY = "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"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

input = input("Input your query here: ")

payload = {
    "model": "llama3-70b-8192",
    "messages": [
        {"role": "user", "content": input}
    ]
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
print("🤖 Groq AI Says:\n", response.json()['choices'][0]['message']['content'])
