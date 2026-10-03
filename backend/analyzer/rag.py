
from vector_search import search_code
from neo4j import GraphDatabase
import ollama


# ==============================
# Neo4j Configuration
# ==============================

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# ==============================
# Get Graph Context
# ==============================

def get_graph_context(function_name):

    query = """
    MATCH (f)
    WHERE (f:Function OR f:Method)
      AND (
          f.name = $name
          OR f.name ENDS WITH "." + $name
      )

    OPTIONAL MATCH (f)-[:CALLS]->(called)
    OPTIONAL MATCH (caller)-[:CALLS]->(f)

    RETURN
        collect(DISTINCT called.name) AS calls,
        collect(DISTINCT caller.name) AS callers
    """

    with driver.session() as session:

        result = session.run(
            query,
            name=function_name
        )

        record = result.single()

        return {
            "calls": record["calls"],
            "callers": record["callers"]
        }


# ==============================
# Ask User
# ==============================

question = input("\nAsk a question about the code: ")


# ==============================
# Semantic Search
# ==============================

chunk, similarity = search_code(question)


# ==============================
# Graph Search
# ==============================

graph_result = get_graph_context(
    chunk["name"]
)


# ==============================
# Build RAG Context
# ==============================

context = f"""
FILE:
{chunk["file"]}

CODE ELEMENT:
{chunk["name"]}

TYPE:
{chunk["type"]}

CODE:
{chunk["content"]}

SEMANTIC SIMILARITY:
{similarity}

GRAPH INFORMATION:

Functions/Methods called by this element:
{graph_result["calls"]}

Functions/Methods that call this element:
{graph_result["callers"]}
"""


# ==============================
# RAG Prompt
# ==============================

prompt = f"""
You are an AI software reverse-engineering assistant.

Answer the user's question using ONLY the software
context provided below.

Do not invent code or relationships that are not present
in the provided context.

If the context is insufficient, clearly say that the
available project context is insufficient.

SOFTWARE CONTEXT:
{context}

USER QUESTION:
{question}

Give a clear and concise explanation.
"""


# ==============================
# Send Context to Qwen
# ==============================

response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)


# ==============================
# Display Result
# ==============================

print("\n===================================")
print("RAG ANSWER")
print("===================================")

print(response["message"]["content"])


# ==============================
# Close Neo4j
# ==============================

driver.close()