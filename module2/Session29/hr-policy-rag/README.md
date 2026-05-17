# HR Policy RAG Assistant

An AI-powered HR Policy Assistant that uses Retrieval-Augmented Generation (RAG) to accurately answer employee questions based on InnoTech Solutions' internal policies.

## Overview
Employees often ask repetitive questions about company policies. Instead of relying on a Large Language Model's general knowledge (which can hallucinate or give generic answers), this assistant retrieves the exact company policy and generates a grounded response. 

It handles policies regarding:
- Leave (Annual & Sick)
- Work From Home (WFH)
- Appraisals
- Code of Conduct

## Architecture
The assistant uses the following tech stack:
- **Python**: Core logic orchestration.
- **Google GenAI SDK (Gemini)**: Used for generating vector embeddings (`gemini-embedding-2`) and generating the final text answer (`gemini-2.5-flash`).
- **ChromaDB**: The local vector database used to store and query the embedded policy chunks.
- **python-dotenv**: To securely load environment variables.

## Setup Instructions

### 1. Set up a Virtual Environment
```bash
python -m venv venv

# On Windows
source venv/Scripts/activate
# On Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Ensure you have a `.env` file in the root directory of this project containing your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## How to Run

Execute the main script:
```bash
python hr_policy_rag.py
```

### Execution Flow
1. **Database Setup**: Initializes a ChromaDB persistent client locally (`./chroma_db`).
2. **Indexing**: Embeds the 4 defined HR policies and upserts them into ChromaDB.
3. **Retrieval**: Takes predefined employee queries, embeds them, and fetches the top relevant chunks from the database based on cosine similarity.
4. **Generation**: Builds a strict prompt containing ONLY the retrieved context and instructs Gemini to answer the question without guessing.
5. **Side-by-side Comparison**: The script finishes by printing a comparison of a raw LLM hallucinating an answer versus the RAG-grounded system accurately answering directly from the policy context.
