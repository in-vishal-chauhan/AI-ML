from services.pinecone_service import PineconeService

API_KEY = "pcsk_4WSKvx_LgSsM6Ps24aszBAVSty7qLR6bhVWJ9416ZuBbceNhsMtFiv2W6x6T6N6dENQUHE"
INDEX_NAME = "quickstart-py"
NAMESPACE = "example-namespace"

service = PineconeService(api_key=API_KEY, index_name=INDEX_NAME, namespace=NAMESPACE)
service.init_index()

# First-time insert
# service.upsert_documents(records)  # <-- Uncomment only when inserting

# Search
query = "who developed theory of relativity"
results = service.search(query, top_k=1)