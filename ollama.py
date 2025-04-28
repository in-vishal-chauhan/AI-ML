llm_config = {
    "model": "gemma3:4b",
    "base_url": "http://127.0.0.1:11434/v1",
    "api_key": "ollama",
    "price": [0,0]
}

from pathlib import Path
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor

# Setting up the code executor
workdir = Path("coding")
workdir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=workdir)

# Setting up the agents

# The UserProxyAgent will execute the code that the AssistantAgent provides
user_proxy_agent = UserProxyAgent(
    name="User",
    code_execution_config={"executor": code_executor},
    is_termination_msg=lambda msg: "FINISH" in msg.get("content"),
)

system_message = """You are a helpful AI assistant who writes code and the user
executes it. Solve tasks using your python coding skills.
In the following cases, suggest python code (in a python coding block) for the
user to execute. When using code, you must indicate the script type in the code block.
You only need to create one working sample.
Do not suggest incomplete code which requires users to modify it.
Don't use a code block if it's not intended to be executed by the user. Don't
include multiple code blocks in one response. Do not ask users to copy and
paste the result. Instead, use 'print' function for the output when relevant.
Check the execution result returned by the user.

If the result indicates there is an error, fix the error.

IMPORTANT: If it has executed successfully, ONLY output 'FINISH'."""

# The AssistantAgent, using the Ollama config, will take the coding request and return code
assistant_agent = AssistantAgent(
    name="Ollama_Assistant",
    system_message=system_message,
    llm_config=llm_config,
)

chat_result = user_proxy_agent.initiate_chat(
    recipient=assistant_agent,
    message="write code to make calculator",
)