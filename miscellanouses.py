from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Hello world")
print("Embedding dimension:", len(embedding))
print("First 5 values:", embedding[:5])