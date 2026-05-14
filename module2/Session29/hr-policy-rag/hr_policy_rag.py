import os
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: Neither GEMINI_API_KEY nor GOOGLE_API_KEY found in environment variables.")
    # Exit or handle as needed, but for now we let it fail gracefully later
else:
    genai.configure(api_key=api_key)

# Step 1 — Define Your HR Policy Documents
POLICY_DOCUMENTS = [
    {
        "id": "policy_leave",
        "text": "Employees are entitled to 20 days of annual leave per calendar year. Sick leave is capped at 10 days annually with medical certification required for more than 2 consecutive days. Unused annual leave can carry forward up to 5 days into the next year.",
        "metadata": {"category": "Leave", "source": "HR Manual 2024"}
    },
    {
        "id": "policy_wfh",
        "text": "Employees can work from home for up to 2 days per week. Eligibility is based on 3 months of tenure and a satisfactory performance rating. All WFH requests must be approved by the immediate manager via the HR portal by Friday of the preceding week.",
        "metadata": {"category": "Work From Home", "source": "Remote Work Policy"}
    },
    {
        "id": "policy_appraisal",
        "text": "The annual appraisal cycle is conducted every April. Performance is rated on a scale of 1 to 5, where 5 is exceptional. Salary increments and bonuses are directly linked to these ratings and company performance.",
        "metadata": {"category": "Appraisal", "source": "Compensation Policy"}
    },
    {
        "id": "policy_conduct",
        "text": "All employees must maintain professional behavior and respect diversity in the workplace. Data privacy is paramount; unauthorized sharing of company data is strictly prohibited. Conflicts of interest must be disclosed to HR immediately upon discovery.",
        "metadata": {"category": "Code of Conduct", "source": "Ethics Handbook"}
    }
]

# Step 2 — Build These Functions

def create_embeddings(texts):
    """Send text list to Gemini embedding model and return embedding vectors."""
    if isinstance(texts, str):
        texts = [texts]
    
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=texts,
        task_type="retrieval_document"
    )
    return result['embeddings']

def setup_vector_database():
    """Create a ChromaDB PersistentClient with a collection using cosine similarity."""
    client = chromadb.PersistentClient(path="./chroma_hr_policy_db")
    # Use cosine similarity as requested
    collection = client.get_or_create_collection(
        name="hr_policy_collection",
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def index_hr_documents(collection):
    """Index your 4 HR policy documents into ChromaDB using upsert."""
    ids = [doc["id"] for doc in POLICY_DOCUMENTS]
    texts = [doc["text"] for doc in POLICY_DOCUMENTS]
    metadatas = [doc["metadata"] for doc in POLICY_DOCUMENTS]
    embeddings = create_embeddings(texts)
    
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print(f"Successfully indexed {len(ids)} documents.")

def retrieve_hr_content(collection, query, top_k=3):
    """Embed the query, search ChromaDB, and return top-K chunks with text, metadata, and distance."""
    query_embedding = create_embeddings([query])[0]
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    chunks = []
    for i in range(len(results['ids'][0])):
        chunks.append({
            "text": results['documents'][0][i],
            "metadata": results['metadatas'][0][i],
            "distance": results['distances'][0][i]
        })
    return chunks

def build_grounded_prompt(query, chunks):
    """Assemble a prompt that injects retrieved chunks as context."""
    context = "\n\n".join([f"Source: {c['metadata']['source']}\nContent: {c['text']}" for c in chunks])
    
    prompt = f"""
You are an HR Policy Assistant at InnoTech Solutions. Use the provided policy context to answer the user's question.
If the context does not contain enough information to answer the question, state that you don't have that information in the company policies.
Do not guess or use outside knowledge.

Context:
{context}

Question: {query}

Answer:"""
    return prompt

def generate_answer(query, chunks):
    """Call Gemini LLM with the grounded prompt and return the response text."""
    prompt = build_grounded_prompt(query, chunks)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_answer_without_retrieval(query):
    """Generate answer without RAG for comparison."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Answer the following question as an HR assistant for a company called InnoTech Solutions: {query}"
    response = model.generate_content(prompt)
    return response.text

def answer_with_rag(collection, query, top_k=3):
    """The complete pipeline: retrieve → print chunks → generate answer."""
    print(f"\n--- Query: {query} ---")
    chunks = retrieve_hr_content(collection, query, top_k)
    
    print("\n[Retrieved Chunks]")
    for i, chunk in enumerate(chunks):
        print(f"{i+1}. [{chunk['metadata']['category']}] (Dist: {chunk['distance']:.4f}): {chunk['text'][:100]}...")
    
    answer = generate_answer(query, chunks)
    print("\n[RAG Answer]")
    print(answer)
    return answer

# Main Execution
if __name__ == "__main__":
    # Setup and Index
    hr_collection = setup_vector_database()
    index_hr_documents(hr_collection)
    
    # Step 3 — Test With Employee Queries
    test_queries = [
        "How many days of annual leave am I entitled to per year?",
        "Do I need manager approval before working from home?",
        "When is the appraisal cycle conducted and how is the increment decided?"
    ]
    
    for q in test_queries:
        answer_with_rag(hr_collection, q)
    
    # Step 4 — Side-by-Side Comparison
    print("\n" + "="*50)
    print("SIDE-BY-SIDE COMPARISON")
    print("="*50)
    
    comp_query = "What is the policy on carrying forward unused leave?"
    
    print(f"\nQUERY: {comp_query}")
    
    print("\n>>> WITHOUT RAG (Generative Only):")
    print(generate_answer_without_retrieval(comp_query))
    
    print("\n>>> WITH RAG (Policy Grounded):")
    answer_with_rag(hr_collection, comp_query)
