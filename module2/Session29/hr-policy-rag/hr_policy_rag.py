import os
import chromadb
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize Gemini Client
client = genai.Client()

# Step 1: Define HR Policy Documents
POLICY_DOCUMENTS = [
    {
        "id": "leave_policy",
        "text": "Employees are entitled to 20 days of annual leave and 10 days of sick leave per calendar year. A maximum of 5 annual leave days can be carried forward to the next year. Sick leave cannot be carried forward.",
        "metadata": {"category": "Leave", "source": "HR Handbook 2024"}
    },
    {
        "id": "wfh_policy",
        "text": "Employees are permitted to work from home for up to 2 days per week. Eligibility requires completing the 90-day probationary period. All WFH requests must be approved by the direct manager at least 48 hours in advance.",
        "metadata": {"category": "Work From Home", "source": "HR Handbook 2024"}
    },
    {
        "id": "appraisal_policy",
        "text": "The appraisal cycle is conducted annually in January. Employees are rated on a scale of 1 to 5. A rating of 4 or 5 guarantees a performance increment, while a rating of 3 requires a secondary review. Ratings of 1 or 2 do not receive an increment.",
        "metadata": {"category": "Appraisal", "source": "HR Handbook 2024"}
    },
    {
        "id": "code_of_conduct_policy",
        "text": "Employees must maintain professional workplace behavior and protect all confidential company data. Any potential conflict of interest, including side business ventures, must be immediately declared to HR for review.",
        "metadata": {"category": "Code of Conduct", "source": "HR Handbook 2024"}
    }
]

# Step 2: Build the required functions
import time

def create_embeddings(texts):
    """Generate embeddings for a list of texts."""
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model="gemini-embedding-2",
            contents=text
        )
        embeddings.append(result.embeddings[0].values)
        time.sleep(1) # Prevent rate limiting
    return embeddings

def setup_vector_database():
    """Initialize ChromaDB and return the collection."""
    db_client = chromadb.PersistentClient(path="./chroma_db")
    collection = db_client.get_or_create_collection(
        name="hr_policy_collection",
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def index_hr_documents(collection):
    """Index documents into the ChromaDB collection."""
    texts = [doc["text"] for doc in POLICY_DOCUMENTS]
    ids = [doc["id"] for doc in POLICY_DOCUMENTS]
    metadatas = [doc["metadata"] for doc in POLICY_DOCUMENTS]
    
    embeddings = create_embeddings(texts)
    
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print(f"Successfully indexed {len(POLICY_DOCUMENTS)} documents.")

def retrieve_hr_content(collection, query, top_k=3):
    """Retrieve top_k relevant documents for the given query."""
    # We query top_k matching chunks
    query_embedding = create_embeddings([query])[0]
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results

def build_grounded_prompt(query, chunks):
    """Assemble a prompt injecting retrieved chunks as context."""
    context_text = "\n\n".join(chunks['documents'][0])
    
    prompt = f"""You are an HR Policy Assistant for InnoTech Solutions.
Answer the following question using ONLY the context provided below.
If the context does not contain the answer, politely state that you cannot find the answer in the policies instead of guessing.

Context:
{context_text}

Question: {query}"""
    return prompt

def generate_answer(query, chunks):
    """Generate the answer using the grounded prompt."""
    prompt = build_grounded_prompt(query, chunks)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def answer_with_rag(collection, query, top_k=3):
    """Complete pipeline: retrieve -> print -> generate."""
    print(f"\n--- Processing Query: '{query}' ---")
    chunks = retrieve_hr_content(collection, query, top_k)
    
    print("\n[Retrieved Context]")
    for i, (doc, metadata, distance) in enumerate(zip(chunks['documents'][0], chunks['metadatas'][0], chunks['distances'][0])):
        print(f"Chunk {i+1} (Distance: {distance:.4f}):")
        print(f"Text: {doc}")
        print(f"Metadata: {metadata}\n")
        
    answer = generate_answer(query, chunks)
    print(f"[RAG Answer]\n{answer}\n")
    return answer

def generate_answer_without_retrieval(query):
    """Baseline answer generated purely from memory without RAG."""
    prompt = f"""You are an HR Policy Assistant for InnoTech Solutions.
Answer the following question: {query}"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# Step 3 & 4: Execution Flow
if __name__ == "__main__":
    print("Setting up Vector Database...")
    collection = setup_vector_database()
    
    print("Indexing Documents...")
    index_hr_documents(collection)
    
    # 3 Queries
    queries = [
        "How many days of annual leave am I entitled to per year?",
        "Do I need manager approval before working from home?",
        "When is the appraisal cycle conducted and how is the increment decided?"
    ]
    
    for q in queries:
        answer_with_rag(collection, q, top_k=2)

    # Step 4: Side-by-Side Comparison
    print("\n=======================================================")
    print("SIDE-BY-SIDE COMPARISON")
    print("=======================================================\n")
    comparison_query = "What happens if I receive a performance rating of 3 in the appraisal cycle?"
    
    print("1. [ANSWER WITHOUT RAG (Hallucination/Generic)]")
    no_rag_answer = generate_answer_without_retrieval(comparison_query)
    print(no_rag_answer)
    print("\n-------------------------------------------------------")
    
    print("2. [ANSWER WITH RAG (Grounded in Policy)]")
    answer_with_rag(collection, comparison_query, top_k=2)