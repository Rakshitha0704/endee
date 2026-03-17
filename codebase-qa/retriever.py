import os
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer('all-MiniLM-L6-v2')
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_embedding(text):
    embedding = model.encode(text)
    return embedding.tolist()

def retrieve_relevant_chunks(question, collection, top_k=5):
    question_embedding = get_embedding(question)
    results = collection.query(
        vector=question_embedding,
        top_k=top_k
    )
    return results

def build_prompt(question, retrieved_chunks):
    context = ""
    for i, chunk in enumerate(retrieved_chunks):
        file_name = chunk['meta'].get("file", "unknown")
        content = chunk['meta'].get("content", "")
        context += f"\n--- Chunk {i+1} from {file_name} ---\n{content}\n"

    prompt = f"""You are a helpful code assistant.
A user has a question about a codebase.
Use the following retrieved code chunks to answer the question accurately.
Always mention which file the answer comes from.

Retrieved code chunks:
{context}

User question: {question}

Answer:"""
    return prompt

def get_answer(question, collection):
    retrieved_chunks = retrieve_relevant_chunks(question, collection)
    prompt = build_prompt(question, retrieved_chunks)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful code assistant who answers questions about codebases clearly and concisely."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content
    return answer, retrieved_chunks
