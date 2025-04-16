import requests

def convert_to_structured_prompt(user_input: str) -> dict:
    # Very basic rule-based logic for now
    return {
        "task": "explain" if "explain" in user_input.lower() else "summarize",
        "style": "bullet-points" if "points" in user_input.lower() else "paragraph",
        "tone": "simple",
        "audience": "general public",
        "language": "English",
        "input": user_input
    }

def send_to_groq(structured_prompt, api_key):
    prompt_text = (
        f"Task: {structured_prompt['task']}\n"
        f"Style: {structured_prompt['style']}\n"
        f"Tone: {structured_prompt['tone']}\n"
        f"Audience: {structured_prompt['audience']}\n"
        f"Language: {structured_prompt['language']}\n"
        f"Text:\n{structured_prompt['input']}\n"
        f"Provide the response in the requested style and language."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",  # or llama3
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.5
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}\n{response.text}"

# === Try it out ===
user_input = input("Enter your question or instruction: ")
api_key = "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"

structured = convert_to_structured_prompt(user_input)
output = send_to_groq(structured, api_key)

print("\n=== Response from Groq ===")
print(output)
