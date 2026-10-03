import os
import ast
from sentence_transformers import SentenceTransformer


PROJECT_PATH = "sample_project"

# Load pre-trained embedding model
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


# Create chunks from the project
all_chunks = []

for root, dirs, files in os.walk(PROJECT_PATH):

    for file in files:

        if file.endswith(".py"):

            file_path = os.path.join(root, file)

            chunks = create_chunks(file_path)

            all_chunks.extend(chunks)


# Create embeddings
print("Creating embeddings...\n")

for i, chunk in enumerate(all_chunks, 1):

    embedding = model.encode(chunk["content"])

    print("------------------------------")
    print("Chunk:", i)
    print("File:", chunk["file"])
    print("Name:", chunk["name"])
    print("Type:", chunk["type"])
    print("Embedding size:", len(embedding))
    print("First 5 values:", embedding[:5])