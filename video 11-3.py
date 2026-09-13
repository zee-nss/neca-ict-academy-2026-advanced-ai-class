from supabase import create_client
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize

supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_SERVICE_KEY'))

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
groq_client =Groq(api_key = os.environ.get('GROQ_API_KEY'))

print('System Initialized')
print('Supabase Connected')
print('Embedding model loaded')
print('Groq client ready')

# Document Processing

def chunk_text(text, chunk_size = 500, overlap = 50):
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Try to break the sentence boundaries
        if end < len(text):
            last_period = text.rfind('.', start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
            chunk = text [start:end].strip()
            if len(chunk) > 20:
                chunks.append(chunk)
            start = end - overlap
        return chunks
# Test Chunk
sample_text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four." * 20
chunks = chunk_text(sample_text)

print()
print('Chunking text:')
print('Original length:', len(sample_text))
print('Number of chunks:', len(chunks))
print('First chunk length:', len(chunks[0]))

# Ingest Documents

def ingest_document(title,content,source):
    print()
    print("Ingesting:", title)
    print("="*40)

    chunks = chunk_text(content)
    stored = 0

    for i, chunk in enumerate(chunks):

        # Generate embeddings
        embedding = embedding_model.encode(chunk).tolist()

        #Store in supabase
        supabase.table('documents').insert(
            {'title': title,
             'content': content,
             'source': source,
             'page_number' : i + 1,
             'embedding' : embedding}
        ).execute()

        stored += 1
    print("Stored", stored, "chunks from", title)
    return stored

# RAG Search

def rag_search(question, top_k = 5):
    #Embed the question
    query_embedding = embedding_model.encode(question).tolist()

    #Search in supabase
    results = supabase.rpc(
        'match_documents',
        {'query_embedding':query_embedding,
         'match_threshold': 0.0,
         'match_count' : top_k}
    ).execute()
    return results.data


# RAG Generate
def rag_generate(question, documents):
    #Build context from documents 
    context = ""
    for i, doc in enumerate(documents):
        context += "Source: " + doc['title'] + " (chunk " + str(doc['page_number']) + ")\n"
        context += doc['content'] + "\n"
        if i < len(documents) - 1:
            context += "\n--\n\n"

    # Generate Answers
    response = groq_client.chat.completions.create(
        model = "openai/gpt-oss-120b",
        messages = [
            {"role": "system", "content" : "Answer questions based ONLY on the provided documents. Cite sources as [Document Title]. If the documents don't contain the answer, say 'I don't have information about that in my knowledge base.' Be concise but complete."},
            {"role": "user", "content": "Documents:\n" + context + "\n\nQuestion: " + question}
        ], temperature = 0.2)
    return response.choices[0].message.content


#Full Rag Pipeline

def full_rag(question):
    print()
    print('Question:', question)
    print("="*50)

    #Step 1: Search
    print("Searching for relevant documents...")
    docs = rag_search(question)

    if not docs:
        print("No relevant documents found.")
        return {"answer" : "I don't have information about that in my knowledge base.", "sources": []}
    print("Found", len(docs), "relevant chunks")

    for doc in docs:
        print(" -", doc['title'], "(similarity: " + str(round(doc['similarity'], 3)) + ")")

    # Step 2: Create
    print()
    print('Generating answer...')
    answer = rag_generate(question, docs)

    # Step 3: Collect sources
    sources = []
    for doc in docs:
        sources.append({
            "title": doc['title'], 
            "chunk": doc['page_number'],
            "similarity": round(doc['similarity'], 3)
        })
    print()
    print("Answer:")
    print(answer)
    print()
    print('Sources:')
    for source in sources:
        print(" -", source['title'], "(chunk " + str(source['chunk']) + ")")
    return { "answer": answer, "sources" : sources}

# Test Documents

#Store documents
print("Storing documents")
print("="*50)

#Document 1: HR Policies
hr_content = """ 
Parental Leave Policy: Employees with one year or more of tenure recieves sixteen weeks of paid parental leave. This applies to both birth and adoption. The leave must be taken within twelve months of the birth or adoption event.

Vacation Policy: Employees recieve fifteen days of paid vacation per year. This increases to twenty days after five years of service. Unused vacation days can be carried over up to a maximum of ten days.

Sick Leave Policy: Employees recieve ten days of paid sick leave per year. A doctor's note is required for absences longer than three consecutive days.
"""
ingest_document("HR Policies", hr_content, "hr_handbook.txt")

#Document 2: IT Policies
it_content = """
Password Policy: All passwords must be changed every ninety days. Passwords must be at least twelve characters long and include a mix of uppercase, lowercase, numbers, and symbols. Two-factor authentication is required for all company accounts.

Software Installation Policy: Employees may not install software without approval from the IT department. All software must be licensed. Requests for new software should be submitted through the IT helpdesk.

Data Security Policy: Confidential data must never be stored on personal devices. All company data must be backed up to the approved cloud storage solution. Lost or stolen devices must be reported to IT within four hours.
"""

ingest_document("IT Policies", it_content, "it_handbook.txt")

# Document 3: Remote Work
remote_content = """
Remote Work Policy: Remote work is permitted up to three days per week after the probation period of ninety days. Full remote work requires written approval from the employee's manager and the HR department.

Home Office Setup: The company provides a one-time stipend of five hundred dollars for home office equipment. This can be used for monitors, keyboards, chairs, or other ergonomic equipment.

Communication Requirements: Remote employees must be available during core hours of ten AM to three PM. Video conferencing is required for all team meetings. Response to Slack messages should be within two hours during work days.
"""

ingest_document("Remote Work Policies", remote_content, "remote_handbook.txt")


# Test The RAG system
print()
print("="*50)

print("Test 1: Parental leave question")
print("="*50)
result1 = full_rag("How long is parental leave and when can i take it?")

print()
print()
print("=" * 50)
print("Test 2: Password question")
print("=" * 50)
result2 = full_rag("What are the password requirements?")

print()
print()
print("=" * 50)
print("Test 3: Cross-document question")
print("=" * 50)
result3 = full_rag("Can I work from home and what equipment does the company provide?")

print()
print()
print("=" * 50)
print("Test 4: Question with no answer")
print("=" * 50)
result4 = full_rag("What is the company policy on stock options?")