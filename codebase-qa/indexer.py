import os
import hashlib
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

SUPPORTED_EXTENSIONS = ['.py', '.js', '.ts', '.md', '.txt']

def get_files_from_repo(repo_path):
    files = []
    for path in Path(repo_path).rglob('*'):
        if path.suffix in SUPPORTED_EXTENSIONS:
            if 'venv' not in str(path) and 'node_modules' not in str(path):
                files.append(path)
    return files

def chunk_file(file_path, chunk_size=500):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    lines = content.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0

    for line in lines:
        current_chunk.append(line)
        current_size += len(line)
        if current_size >= chunk_size:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

def get_embedding(text):
    embedding = model.encode(text)
    return embedding.tolist()

def index_repository(repo_path, collection):
    print(f"Scanning repository: {repo_path}")
    files = get_files_from_repo(repo_path)
    print(f"Found {len(files)} files to index")

    total_chunks = 0
    batch = []

    for file_path in files:
        chunks = chunk_file(file_path)

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            chunk_id = hashlib.md5(f"{file_path}_{i}".encode()).hexdigest()
            embedding = get_embedding(chunk)

            # Plain dictionary as Endee expects
            batch.append({
                "id": chunk_id,
                "vector": embedding,
                "meta": {
                    "file": str(file_path),
                    "chunk_index": str(i),
                    "content": chunk
                }
            })

            if len(batch) >= 50:
                collection.upsert(input_array=batch)
                total_chunks += len(batch)
                print(f"Indexed {total_chunks} chunks so far...")
                batch = []

    if batch:
        collection.upsert(input_array=batch)
        total_chunks += len(batch)

    print(f"Indexed {total_chunks} chunks successfully!")
    return total_chunks
