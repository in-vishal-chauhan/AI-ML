from services.receptionist import AIReceptionist
from services.groq_service import GroqAPI
# from services.database_service import Database
from services.sqlite_db import SqliteDatabase
# from services.document_qa_service import DocumentQAService
from services.read_store_vector import ReadStoreVector

groq = GroqAPI()
db = SqliteDatabase()
# document_qa_service = DocumentQAService()
read_store_vector = ReadStoreVector()
receptionist = AIReceptionist(groq, db, read_store_vector)

user_query = input("Enter your query: ")
response = receptionist.orchestrator(user_query)
if response is not None:
    print("Response:", response)