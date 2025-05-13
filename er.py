from autogen import AssistantAgent, UserProxyAgent

config_list = [
    {
        "model": "llama3-70b-8192",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "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",
        "price": [0, 0]
    }
]

assistant = AssistantAgent(
    name="groq_assistant",
    llm_config={"config_list": config_list},
    code_execution_config=False
)

user = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: "TERMINATE" in x["content"],
    code_execution_config=False,
)

user.initiate_chat(
    assistant,
    message="Explain quantum computing in simple terms. Then say TERMINATE."
)
