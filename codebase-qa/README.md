# 💻 Codebase Q&A — RAG with Endee Vector Database

Ask any question about a codebase and get accurate answers grounded in the actual source code.

## Demo
> Index any GitHub repo → Ask questions in plain English → Get answers with source file references

---

## What This Project Does
This project is a Retrieval Augmented Generation (RAG) application that lets you:
- Clone any GitHub repository
- Index all its code files into Endee vector database
- Ask natural language questions about the codebase
- Get accurate answers with references to the exact source files

---

## How Endee Is Used
Endee is the core vector database powering this project. Here's exactly where it fits:

1. **Indexing** — Each code file is chunked into 500-character pieces. Each chunk is converted into a 384-dimensional embedding vector using `sentence-transformers`. These vectors are stored in Endee using `collection.upsert()`.

2. **Retrieval** — When a user asks a question, it is embedded into a vector and sent to Endee via `collection.query()`. Endee performs cosine similarity search and returns the top 5 most relevant code chunks.

3. **Generation** — The retrieved chunks are passed as context to the LLM (Groq), which generates a clear answer with source file references.

---

## Demo Video
https://www.loom.com/share/ac9dbcb94f624a4dad06c4b19fcdca14

## System Design
```
User Question
     │
     ▼
Embed Question (sentence-transformers)
     │
     ▼
Query Endee Vector DB (cosine similarity)
     │
     ▼
Top 5 Relevant Code Chunks
     │
     ▼
Build Prompt (chunks + question)
     │
     ▼
Groq LLM (llama-3.3-70b-versatile)
     │
     ▼
Answer + Source References
```

---

## Tech Stack
- **Vector Database** — Endee (local, Docker)
- **Embeddings** — sentence-transformers (all-MiniLM-L6-v2, runs locally, free)
- **LLM** — Groq API (llama-3.3-70b-versatile)
- **UI** — Streamlit
- **Language** — Python 3.10+

---

## Project Structure
```
codebase-qa/
├── app.py              # Streamlit UI
├── indexer.py          # File ingestion, chunking, embedding, Endee upsert
├── retriever.py        # Endee query, prompt building, LLM call
├── requirements.txt    # Dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker Desktop

### 1. Clone this repository
```bash
git clone https://github.com/YOUR-USERNAME/codebase-qa
cd codebase-qa
```

### 2. Start Endee server
```bash
docker run --ulimit nofile=100000:100000 -p 8080:8080 --name endee-server --restart unless-stopped endeeio/endee-server:latest
```

### 3. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### 6. Run the app
```bash
streamlit run app.py
```

### 7. Use the app
1. Clone any GitHub repo to your machine
2. Paste the local path in the sidebar
3. Click **Index Repository**
4. Ask questions about the codebase!

---

## Example Questions
- "What does the @click.command decorator do?"
- "Where are API routes defined?"
- "How is authentication handled?"
- "What does the main function do?"

---

## Endee Repository
- Forked from: https://github.com/endee-io/endee
- My fork: https://github.com/Rakshitha0704/endee
