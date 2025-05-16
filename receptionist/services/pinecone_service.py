from pinecone import Pinecone
from logger import get_logger

logger = get_logger(__name__)

class PineconeService:
    def __init__(self, api_key: str, index_name: str, namespace: str):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.namespace = namespace
        self.index = None

    def init_index(self):
        if not self.pc.has_index(self.index_name):
            self.pc.create_index_for_model(
                name=self.index_name,
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "chunk_text"}
                }
            )
        self.index = self.pc.Index(self.index_name)
        return self.index

    def upsert_documents(self, records: list[dict]):
        self.index.upsert_records(self.namespace, records)

    def search(self, query: str, top_k: int = 3):
        response = self.index.search(
            namespace=self.namespace,
            query={
                "top_k": top_k,
                "inputs": {"text": query}
            }
        )
        return response

