import pymysql
from dotenv import load_dotenv
import os
import autogen

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "price": [0,0]
}
 
load_dotenv()
 
def find_rate(color, material, quality):
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection:
            with connection.cursor() as cursor:
                sql = """
                SELECT rate FROM products
                WHERE LOWER(color) = LOWER(%s)
                  AND LOWER(material) = LOWER(%s)
                  AND LOWER(quality) = LOWER(%s)
                LIMIT 1;
                """
                cursor.execute(sql, (color, material, quality))
                result = cursor.fetchone()
                return result["rate"] if result else "No rate found."
    except Exception as e:
        return f"Error: {str(e)}"

productInfoAskAgent = autogen.ConversableAgent(
    name="Product_Info_Ask_Agent",
    system_message=(
        "You are an assistant whose sole purpose is to collect specific product details from the user. "
        "Your task is to ask the user for the **color**, **material**, and **quality** of the product they are interested in. "
        "Once you have received all three details, immediately call the `find_rate` function using the provided information. "
        "Then, respond to the user with the rate of the product. "
        "Do not ask any other questions or engage in unrelated conversation. "
        "Strictly follow these instructions and do not deviate from them."
    ),
    llm_config=llm_config,
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

userAgent = autogen.UserProxyAgent(
    name="UserAgent",
    llm_config=False,
    code_execution_config=False,
    human_input_mode="ALWAYS",
)