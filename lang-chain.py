import ast  # To safely evaluate string input to list
from langchain.agents import Tool, initialize_agent
from langchain_groq import ChatGroq

# ----------- Tool Functions -----------

def recommend_outfits(input: str):
    print(f"[Tool: Recommend] Input: {input}")
    # Stub: Always recommends two kurtas
    return ["kurta123", "kurta456"]

def check_inventory(input: str):
    print(f"[Tool: Inventory] Checking: {input}")
    try:
        outfit_ids = ast.literal_eval(input)  # Convert input string to list
        return {outfit_id: (outfit_id != "kurta456") for outfit_id in outfit_ids}
    except Exception as e:
        return {"error": f"Invalid input format for inventory: {str(e)}"}

def get_price(input: str):
    print(f"[Tool: Price] Getting prices for: {input}")
    try:
        outfit_ids = ast.literal_eval(input)
        return {outfit_id: "₹1999" for outfit_id in outfit_ids}
    except Exception as e:
        return {"error": f"Invalid input format for pricing: {str(e)}"}

# ----------- Register Tools -----------

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

# ----------- Initialize LLM + Agent -----------

# Requires GROQ_API_KEY to be set as environment variable
llm = ChatGroq(model="llama3-70b-8192", api_key="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")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    verbose=True,
)

# ----------- Agent Query -----------

query = "I want a blue casual kurta under ₹2000 that’s in stock."
response = agent.run(query)
print("\nFinal Response:", response)
