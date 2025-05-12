import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. Prepare the data
texts = ["apple is a fruit", "python is a language", "the sun is bright"]

# 2. Convert text to vectors using SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
vectors = model.encode(texts)

# 3. Create a FAISS index
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)

# 4. Add vectors to the index
index.add(np.array(vectors))

# 5. Save the index
faiss.write_index(index, "my_index.faiss")

# Load index
index = faiss.read_index("my_index.faiss")

# Query
query = model.encode(["programming language"])
D, I = index.search(np.array(query), k=2)

print("Results:", I)
print("Distances:", D)