from services.receptionist import AIReceptionist
from services.groq_service import GroqAPI
from services.database_service import Database

groq = GroqAPI()
db = Database()
receptionist = AIReceptionist(groq, db)

user_query = input("Enter your query: ")
response = receptionist.handle_query(user_query)
print("Response:", response)