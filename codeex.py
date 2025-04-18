from autogen import ConversableAgent
from autogen.coding import CodeBlock, LocalCommandLineCodeExecutor

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "price": [0, 0]
}

executor = LocalCommandLineCodeExecutor(
    timeout=10,
    work_dir="coding",
)

agent = ConversableAgent(
    name="SmartAgent",
    llm_config=llm_config,
    system_message="You are a helpful Python assistant. "
    "without comments",
    human_input_mode="ALWAYS",
    code_execution_config={"executor": executor},
)

math_task = input('Press Enter math calculation question.')

reply = agent.generate_reply(messages=[{"role": "user", "content": math_task}])
print(reply)
print(executor.execute_code_blocks(code_blocks=[CodeBlock(language="python", code=reply),]))
