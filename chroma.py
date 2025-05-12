import chromadb
from sentence_transformers import SentenceTransformer

# 1. Initialize the Chroma client
client = chromadb.Client()

# 2. Create a collection to store vectors
collection = client.create_collection(name="paragraphs_collection")

# 3. Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 4. Define a paragraph (direct text input)
paragraph = "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals."

# 5. Convert the paragraph into a vector using the model
vector = model.encode([paragraph])[0]  # Get the vector for the paragraph

# 6. Store the paragraph and vector in the Chroma database
collection.add(
    documents=[paragraph],
    metadatas=[{"source": "ai_paragraph"}],
    ids=["ai_paragraph_1"],
    embeddings=[vector]
)

# 7. Query the vector database with a similar query
query = "What is artificial intelligence?"
query_vector = model.encode([query])

# Perform the search and return the most similar paragraph
results = collection.query(
    query_embeddings=query_vector,
    n_results=1
)

# Display the result
print("Query:", query)
print("\nMost Similar Paragraph:", results['documents'][0])
