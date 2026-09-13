from supabase import create_client
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

#Connecting to supabase

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Clear existing documents (for testing)
supabase.table('documents').delete().gt('id', 0).execute()
print("Cleared existing documents")

#Load the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

#Load the groq client
groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

print("Connected to Supabase")
print("Embedding Model loadel")
print('Groq Client Ready')

#Store Document with Embedding

def store_document(title, content, source, page_number=1): #This will store a document chunk with its supabase embedding
    #Generate embedding locally
    embedding =  embedding_model.encode(content).tolist()

    #Insert into Supabase
    result = supabase.table('documents').insert({'title':title, 'content':content, 'source': source, 'page_number': page_number, 'embedding':embedding}).execute()
    print("Stored:", title)
    return result.data

#Search for similar document
def search_similar(query, top_k=5, threshold=0.0):
    query_embedding = embedding_model.encode(query).tolist()
    result = supabase.rpc('match_documents', {
        'query_embedding': query_embedding,
        'match_threshold': threshold,
        'match_count': top_k
    }).execute()
    return result.data



#Complete RAG Query
def rag_query(question):
    print()
    print('Question:',question)
    print("="*40)

    #Search for relevant document
    docs = search_similar(question)

    if not docs:
        print("No relevant documents found.")
        return "I couldn't find relevant information in our documents."
    print("Found",len(docs), "relevant documents:")
    for d in docs:
        print(" -", d['title'], "(similarity:" + str(round(d['similarity'], 3)) + ")")

    #Build context from retrieved documents
    context = ""
    for d in docs:
        context += "[" + d['title'] + ", page" + str(d["page_number"]) + "]\n"
        context += d['content'] + "\n\n"

    # Generate answer using groq

    response = groq_client.chat.completions.create(model = "openai/gpt-oss-120b", messages = [
        {"role": "system",
         "content" : "Answer the question based ONLY on the provided documents. Cite sources like[Title, page X]. If the documents don't contain the answer, say so."},
        {"role": "user",
         "content": "DOCUMENTS:\n" + context + "\nQUESTION:" + question}], 
         temperature= 0.2
         )
    answer = response.choices[0].message.content

    print()
    print("ANSWER:")
    print(answer)
    return answer

    
# Test it
# Store Sample Documents
print("Storing documents")
print("="*40)
store_document("Employee Handbook", "Employees with one year or more of tenure recieve sixteen weeks of paid parental leave. This applies to both birth and adoption,", "handbook.pdf", 42)
store_document("IT Policy", "Passwords must be changed every 90 days. Two-factor authentication is required for all company accounts.", "it_policy.pdf", 15)
store_document("Remote Work Policy", "Remote work is permitted up to three days per week after the probation period. Full remote requires manager approval.", "remote_policy.pdf", 3)
store_document("Benefit Guide", "Health insurance covers maternity and prenatal care, Dental and vision plans are available as add-ons.", "benefits.pdf", 22)
store_document("Office Guide", "The office cafeteria serves hot lunch from Monday to Friday. Pizza Friday is a company tradition.", "office_guide.pdf", 8)

print()
print("=" * 50)
print("MANUAL SUPABASE TEST")
print("=" * 50)

# Count documents
count = supabase.table('documents').select('id', count='exact').execute()
print("Documents in table:", count.count)

# Try match_documents directly with threshold 0
test_embedding = embedding_model.encode("parental leave").tolist()
print("Test embedding length:", len(test_embedding))

result = supabase.rpc('match_documents', {
    'query_embedding': test_embedding,
    'match_threshold': 0.0,
    'match_count': 5
}).execute()

print("RPC result:", result.data)
print("Number of results:", len(result.data) if result.data else 0)
print()
print("="*50)
print("Test 1: HR Question")
print("="*50)
rag_query("What is the parental leave policy?")

print()
print()
print("="*50)
print("Test 2: IT Question")
print("="*50)
rag_query("How often do i need to change my password?")

print()
print()
print("="*50)
print("Test 3: Question with no answer in the documents")
print("="*50)
rag_query("What is the company policy on stock options")