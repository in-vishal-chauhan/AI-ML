from autogen import ConversableAgent, AssistantAgent, GroupChat, GroupChatManager

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "price": [0, 0]
}

# 🧑 Admin Agent - the user
admin = ConversableAgent(
    name="Admin",
    llm_config=llm_config,
    human_input_mode="ALWAYS",
    system_message="Give a math task and review the result."
)

# 🧠 Planner - analyzes the task
planner = ConversableAgent(
    name="Planner",
    llm_config=llm_config,
    system_message="Analyze the user's math problem, break it down into steps, "
                   "and instruct the Engineer to solve it using Python code."
)

engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    description="Engineer that writes Python code to solve the math task.",
    system_message="Always respond with Python code inside triple backticks ```python ...```"
)

# ⚙️ Executor - runs code
executor = ConversableAgent(
    name="Executor",
    human_input_mode="NEVER",
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "calculator_workspace",
        "use_docker": False
    },
    system_message="Execute the code and report the result."
)

# 📘 Explainer - interprets the result
explainer = ConversableAgent(
    name="Explainer",
    llm_config=llm_config,
    system_message="Explain how the result was computed, step-by-step, like a math tutor."
)

# 💬 GroupChat
groupchat = GroupChat(
    agents=[admin, planner, engineer, executor, explainer],
    messages=[],
    max_round=10
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config
)

# 🎯 Start a sample chat
math_task = "What is 25 squared plus 12?"

admin.initiate_chat(
    manager,
    message=math_task
)
