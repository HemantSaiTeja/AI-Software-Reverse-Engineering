import os
import ast


PROJECT_PATH = "sample_project"


def chunk_python_file(file_path):
    chunks = []

    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    for node in ast.walk(tree):

        # Normal functions
        if isinstance(node, ast.FunctionDef):

            # Check whether it is inside a class
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
                "start_line": start_line,
                "end_line": end_line,
                "content": code
            })

    return chunks


all_chunks = []

for root, dirs, files in os.walk(PROJECT_PATH):

    for file in files:

        if file.endswith(".py"):

            file_path = os.path.join(root, file)

            chunks = chunk_python_file(file_path)

            all_chunks.extend(chunks)


print("Code chunks created:", len(all_chunks))

for i, chunk in enumerate(all_chunks, 1):

    print("\n------------------------------")
    print("Chunk", i)
    print("File:", chunk["file"])
    print("Type:", chunk["type"])
    print("Class:", chunk["class"])
    print("Name:", chunk["name"])
    print("Lines:", chunk["start_line"], "-", chunk["end_line"])
    print("Content:")
    print(chunk["content"])