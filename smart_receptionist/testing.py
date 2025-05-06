from services.receptionist import AIReceptionist
from services.groq_service import GroqAPI
from services.database_service import Database
from services.document_qa_service import DocumentQAService

groq = GroqAPI()
db = Database()
document_qa_service = DocumentQAService()
receptionist = AIReceptionist(groq, db, document_qa_service)

user_query = input("Enter your query: ")
response = receptionist.orchestrator(user_query)
print("Response:", response)