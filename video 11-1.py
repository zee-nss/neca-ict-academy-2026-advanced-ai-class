from sentence_transformers import SentenceTransformer
import numpy as np


# Load the Embeddings

model = SentenceTransformer('all-MiniLM-L6-v2')

print("Embedding model loaded")
print("Model:", model.get_sentence_embedding_dimension(),"dimensions")

#Generate Embeddings
def get_embedding(text):
    return model.encode(text)

#Test texts- related and unrelated
texts= ["Parental leave policy for new parents", "Maternity and paternity benefits", "How to make pizza at home", "Employee vacation policy","Pizza delivery near me"]
print()
print("Generating Embeddings")
print("="*40)

embeddings = {}
for text in texts:
    embeddings[text] = get_embedding(text)
    print ("Embedding:", text)
    print("Vector dimension:",len(embeddings[text]))
    print("First 3 values:", [round(v, 4) for v in embeddings[text][:3]])
    print()

# Compute Similarity
def cosine_similarity(vec1, vec2): #Calculate the cosine similarity between the two vectors
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)
#Compare parental leave with everything
query_text = "Parental leave policy for new parents"
query_embedding = embeddings[query_text]
print()
print("Similarity To:", query_text)
print("="*40)
print()

for text, embedding in embeddings.items():
    similarity = cosine_similarity(query_embedding, embedding)
    print(" "+str(round(similarity, 4)) +"-"+ text)

# Build a simple Vector Database
class SimpleVectorDB: # In-memory vector database for semantic search
    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add(self, text, metadata=None): # Add a document with it's embedding
        embedding = get_embedding(text)
        self.documents.append({"text": text, "metadata": metadata or {}})
        self.embeddings.append(embedding)
        print("Added:",text[:60] + "...")
    def search(self, query, top_k=3): #search for most similar documents.
        query_embedding = get_embedding(query)

        similarities = []
        for i , doc_embedding in enumerate(self.embeddings):
            sim = cosine_similarity(query_embedding, doc_embedding)
            similarities.append((sim, i))
        similarities.sort(reverse = True, key = lambda x: x[0])
        results = []
        for sim, idx in similarities[:top_k]:
            results.append({"similarity": round(sim, 3), "text": self.documents[idx]["text"], "metadata": self.documents[idx]["metadata"]})
        return results
    # Create a knowledge base
print()
print("Building Knowledge Base")
print("="*40)

db = SimpleVectorDB()

db.add("Employees with 1+ year tenure recieve 16 weeks paid parental leave.", {"source": "HR Policy", "page": 42})
db.add("Vacation acrual: 15 days per year, increasing to 20 after 5 years.", {"source": "HR Policy", "page": 15})
db.add("The office cafeteria serves pizza every Friday.", {"source": "Office Guide", "page": 8})
db.add("Health insurance covers maternity and prenatal care.", {"source": "Benefits Guide", "page": 22})

# 'audio', 'image', 'text', 'video'

# Test Semantic Search

print()
print("Search 1: 'How long is maternity leave?'")
print("="*40)
results = db.search("How long is maternity leave?", top_k = 3)
for r in results:
    print(" [" +str(r['similarity']) + "] "+r['text'])
    print("Source:", r['metadata'].get('source'), "Page:", r['metadata'].get('page'))
    print()

print("Search 2: 'Can i work from home?'") 
print("=" *40)
results = db.search("Can i work from home?", top_k= 3)
for r in results:
    print(" [" +str(r['similarity']) + "] "+r['text'])
    print("Source:", r['metadata'].get('source'), "Page:", r['metadata'].get('page'))
    print()

print("Search 3: 'What food is availabe?'") 
print("=" *40)
results = db.search("What food is availabe?", top_k= 3)
for r in results:
    print(" [" +str(r['similarity']) + "] "+r['text'])
    print("Source:", r['metadata'].get('source'), "Page:", r['metadata'].get('page'))
    print()       