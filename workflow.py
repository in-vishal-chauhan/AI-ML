import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType

# Set your API keys securely (you can use .env in production)
# os.environ["OPENAI_API_KEY"] = "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"
# os.environ["SERPAPI_API_KEY"] = "54fe8a5b2230cebbbcd36bce50f589e462296dc998e09c05ca12ff5e1742e4c7"

# Initialize ChatOpenAI (gpt-4 used to simulate gpt-4o-mini)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize memory to retain conversation context
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Calculator Tool
def calculate(query):
    """Useful for solving basic math expressions"""
    try:
        return str(eval(query))
    except Exception as e:
        return f"Error during calculation: {e}"

calculator_tool = Tool(
    name="Calculator",
    func=calculate,
    description="Useful for solving basic math expressions"
)

# SerpAPI Search Tool
search_tool = Tool(
    name="Search",
    func=SerpAPIWrapper().run,
    description="Useful for answering questions about current events or general knowledge"
)

# Combine tools with the LLM into an agent
agent = initialize_agent(
    tools=[calculator_tool, search_tool],
    llm=llm,
    memory=memory,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Example query using both tools
query = "What's 12 * (3 + 2), and what's the current weather in Tokyo?"
response = agent.run(query)

print("\n🧠 Agent Response:\n", response)