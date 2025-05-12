import chromadb
from sentence_transformers import SentenceTransformer
import traceback
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Sample paragraph
    paragraph = "Artificial intelligence is transforming industries by enabling machines to learn from data and make decisions."
    logger.info("Paragraph to store: %s", paragraph)

    # Initialize the embedding model
    logger.info("Loading embedding model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Generate embedding
    logger.info("Generating embedding...")
    embedding = embedding_model.encode(paragraph).tolist()
    logger.debug("Embedding generated: %s (length: %d)", embedding[:5], len(embedding))

    # Initialize ChromaDB client (try in-memory first)
    logger.info("Trying in-memory ChromaDB client...")
    try:
        client = chromadb.Client()  # In-memory client
        logger.debug("In-memory ChromaDB client initialized")
    except Exception as e:
        logger.warning("In-memory client failed: %s. Falling back to persistent client.", str(e))
        # Check storage path for persistent client
        storage_path = "./vector_db"
        logger.info("Checking storage path: %s", storage_path)
        if not os.path.exists(storage_path):
            logger.info("Creating storage directory: %s", storage_path)
            os.makedirs(storage_path)
        if not os.access(storage_path, os.W_OK):
            raise PermissionError(f"No write permission for storage path: {storage_path}")
        client = chromadb.PersistentClient(path=storage_path, settings=chromadb.Settings(anonymized_telemetry=False))
        logger.debug("Persistent ChromaDB client initialized")

    # Create or get a collection
    collection_name = "paragraphs"
    logger.info("Accessing collection: %s", collection_name)
    collection = client.get_or_create_collection(name=collection_name)
    logger.debug("Collection accessed: %s", collection_name)

    # Store the paragraph
    logger.info("Storing paragraph in vector database...")
    logger.debug("Preparing to add: ID=para_1, Document=%s, Embedding length=%d", paragraph[:50], len(embedding))
    collection.add(
        documents=[paragraph],
        embeddings=[embedding],
        ids=["para_1"]
    )
    logger.info("Paragraph stored successfully: %s", paragraph)

    # Query to verify
    logger.info("Querying the database to verify storage...")
    results = collection.query(
        query_embeddings=[embedding],
        n_results=1
    )
    logger.info("Queried result: %s", results['documents'][0][0])

except Exception as e:
    logger.error("An error occurred: %s", str(e))
    logger.error("Stack trace: %s", traceback.format_exc())
    raise

finally:
    logger.info("Script execution completed.")