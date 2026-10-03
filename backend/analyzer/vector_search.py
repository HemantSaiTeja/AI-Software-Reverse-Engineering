import os
import ast
import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_PATH = "sample_project"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_chunks(file_path):
    chunks = []

    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            parent_class = None

            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef):
                    for child in parent.body:
                        if child is node:
                            parent_class = parent.name

            start_line = node.lineno
            end_line = node.end_lineno

            code = "\n".join(
                source_code.splitlines()[start_line - 1:end_line]
            )

            chunks.append({
                "file": file_path,
                "type": "method" if parent_class else "function",
                "class": parent_class,
                "name": node.name,
                "content": code
            })

    return chunks


# -----------------------------
# Create code chunks
# -----------------------------

all_chunks = []

for root, dirs, files in os.walk(PROJECT_PATH):

    for file in files:

        if file.endswith(".py"):

            file_path = os.path.join(root, file)

            chunks = create_chunks(file_path)

            all_chunks.extend(chunks)


# -----------------------------
# Create embeddings
# -----------------------------

texts = []

for chunk in all_chunks:
    texts.append(chunk["content"])


embeddings = model.encode(texts)


# -----------------------------
# Search function
# -----------------------------

def search_code(query):

    query_embedding = model.encode(query)

    similarities = []

    for embedding in embeddings:

        similarity = np.dot(query_embedding, embedding) / (
            np.linalg.norm(query_embedding) *
            np.linalg.norm(embedding)
        )

        similarities.append(similarity)

    # Find highest similarity
    best_index = np.argmax(similarities)

    return all_chunks[best_index], similarities[best_index]


# -----------------------------
# Test search
# -----------------------------

query = "Where is user validation performed?"

result, score = search_code(query)

print("\n==============================")
print("SEARCH QUERY:")
print(query)

print("\nBEST MATCH:")
print("File:", result["file"])
print("Type:", result["type"])
print("Name:", result["name"])
print("Similarity:", score)

print("\nCODE:")
print(result["content"])