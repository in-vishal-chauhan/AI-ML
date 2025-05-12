from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI

# Define tools
def recommend_outfits(input):
    return ["kurta123", "kurta456"]

def check_inventory(input):
    return {"kurta123": True, "kurta456": False}

def get_price(input):
    return {"kurta123": "₹1999"}

tools = [
    Tool(
        name="OutfitRecommender",
        func=recommend_outfits,
        description="Recommends outfits based on user preferences like color, budget, occasion"
    ),
    Tool(
        name="InventoryChecker",
        func=check_inventory,
        description="Checks if the given outfit IDs are in stock"
    ),
    Tool(
        name="PriceFetcher",
        func=get_price,
        description="Gets the price of the given outfit IDs"
    ),
]

# Initialize agent
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", verbose=True)

# Run agent
agent.run("I want a blue casual kurta under ₹2000 that’s in stock.")
