from autogen import ConversableAgent

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "temperature": 0,
    "price": [0, 0]
}

# Agent 1: Echo Agent
echo_agent = ConversableAgent(
    name="Echo_Agent",
    system_message="Just repeat the exact message I send you, no changes.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

# Agent 2: Uppercase Agent
uppercase_agent = ConversableAgent(
    name="Uppercase_Agent",
    system_message="Convert the sentence I send to all UPPERCASE. Return only the result.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

# Agent 3: Reverser Agent
reverser_agent = ConversableAgent(
    name="Reverser_Agent",
    system_message="Reverse the string I give you. No comments or formatting, just the reversed text.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

# Agent 4: Exclaimer Agent
exclaimer_agent = ConversableAgent(
    name="Exclaimer_Agent",
    system_message="Add three exclamation marks at the end of the text I send. Don't add anything else.",
    llm_config=llm_config,
    human_input_mode="NEVER"
)

msg1 = echo_agent.initiate_chat(uppercase_agent, message="hello", max_turns=1).chat_history[-1]['content']
msg2 = echo_agent.initiate_chat(reverser_agent, message=msg1, max_turns=1).chat_history[-1]['content']
msg3 = echo_agent.initiate_chat(exclaimer_agent, message=msg2, max_turns=1).chat_history[-1]['content']
# final = echo_agent.initiate_chat(exclaimer_agent, message=msg3, max_turns=1).chat_history[-1]['content']

# without feedback below
# msg1 = echo_agent.initiate_chat(uppercase_agent, message="hello", max_turns=1).chat_history[-1]['content']
# msg2 = echo_agent.initiate_chat(reverser_agent, message="hello", max_turns=1).chat_history[-1]['content']
# msg3 = echo_agent.initiate_chat(exclaimer_agent, message="hello", max_turns=1).chat_history[-1]['content']
