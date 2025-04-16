import tkinter as tk
from tkinter import scrolledtext
import requests

# === Your Groq API Key (💡 Set it here once) ===
GROQ_API_KEY = "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"  # Replace this with your actual key

# === Convert input to structured prompt ===
def convert_to_structured_prompt(user_input: str) -> dict:
    return {
        "task": "explain" if "explain" in user_input.lower() else "summarize",
        "style": "bullet-points" if "points" in user_input.lower() else "paragraph",
        "tone": "simple",
        "audience": "general public",
        "language": "English",
        "input": user_input
    }

# === Call Groq API ===
def send_to_groq(structured_prompt):
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
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.5
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}\n{response.text}"

# === Run on Button Click ===
def generate_response():
    user_input = input_text.get("1.0", tk.END).strip()

    if not user_input:
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Please enter some input text.")
        return

    structured = convert_to_structured_prompt(user_input)
    result = send_to_groq(structured)

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)

# === GUI Setup ===
root = tk.Tk()
root.title("GenAI Prompt GUI (Groq Powered)")
root.geometry("700x600")

tk.Label(root, text="Enter your question or task:").pack()
input_text = scrolledtext.ScrolledText(root, height=10, width=80)
input_text.pack()

tk.Button(root, text="Generate Response", command=generate_response).pack(pady=10)

tk.Label(root, text="AI Response:").pack()
output_text = scrolledtext.ScrolledText(root, height=15, width=80)
output_text.pack()

root.mainloop()
