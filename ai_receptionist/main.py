import autogen
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

llm_config = {
    "model": "gemma-2-2b-it",
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "temperature": 0,
    "price": [0, 0],
}

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
                if result:
                    return (
                        f"Your inquiry for Color: '{color}', Material: '{material}', "
                        f"Quality: '{quality}' has a rate of ₹{result['rate']}."
                    )
                else:
                    return (
                        f"No rate found for Color: '{color}', Material: '{material}', "
                        f"Quality: '{quality}'."
                    )
    except Exception as e:
        return f"Database error: {str(e)}"

validatorAgent = autogen.ConversableAgent(
    name="ValidatorAgent",
    llm_config=llm_config,
    system_message="""You are a strict validation agent. Verify if an input value is appropriate for a given field:

For COLOR: Must be a standard color name. 
Reject if it's clearly something else (like a material name).

For MATERIAL: Must be a common material.
Reject colors or quality terms.

For QUALITY: Must be a quality descriptor.
Reject colors or materials.

Respond STRICTLY with either:
'valid' - if perfect match for field
'invalid' - if not appropriate for field""",
    human_input_mode="NEVER",
)

inputAgent = autogen.ConversableAgent(
    name="InputAgent",
    llm_config=llm_config,
    system_message="You are the user providing input messages.",
    human_input_mode="NEVER",
)

def get_valid_input(prompt, field_name):
    while True:
        value = input(prompt).strip()
        if not value:
            print(f"Error: {field_name} cannot be empty. Please try again.")
            continue

        validation_prompt = (
            f"Value: '{value}'\nField: {field_name}\n"
            "Is this valid? Respond strictly with 'valid' or 'invalid'."
        )

        validation_response = (
            validatorAgent.generate_reply(
                messages=[{"content": validation_prompt, "role": "user"}],
                sender=inputAgent,
            ).strip().lower()
        )

        if validation_response == "valid":
            return value
        else:
            print(f"Error: '{value}' is not a valid {field_name}. Please try again.")
            if field_name == "color":
                print("Please enter a valid color.")
            elif field_name == "material":
                print("Please enter a valid material.")
            else:
                print("Please enter a valid quality.")

print("Please enter the following details (all fields required):")
color = get_valid_input("Enter color: ", "color")
material = get_valid_input("Enter material: ", "material")
quality = get_valid_input("Enter quality: ", "quality")

db_response = find_rate(color, material, quality)
print(db_response)