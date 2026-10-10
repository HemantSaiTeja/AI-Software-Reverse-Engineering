import sys
import os

ANALYZER_PATH = os.path.join(
    os.path.dirname(__file__),
    "analyzer"
)

sys.path.insert(0, ANALYZER_PATH)


from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from vector_search import search_code
from retriever import get_graph_context
from llm import ask_llm


app = FastAPI(
    title="AI Software Reverse Engineering API"
)


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "AI Software Reverse Engineering API is running"
    }


@app.post("/ask")
def ask_question(data: Question):

    # Get user question
    question = data.question

    # -----------------------------------
    # STEP 1: Semantic Code Search
    # -----------------------------------
    chunk, similarity = search_code(question)

    # -----------------------------------
    # STEP 2: Get Neo4j Graph Context
    # -----------------------------------
    graph_result = get_graph_context(
        chunk["name"]
    )

    # -----------------------------------
    # STEP 3: Ask Qwen3 LLM
    # -----------------------------------
    answer = ask_llm(
        question,
        chunk["content"],
        graph_result["calls"],
        graph_result["callers"]
    )

    # -----------------------------------
    # STEP 4: Return Result
    # -----------------------------------
    return {
        "question": question,
        "answer": answer,
        "file": chunk["file"],
        "name": chunk["name"],
        "type": chunk["type"],

        # Convert NumPy float32 to normal Python float
        "similarity": float(similarity),

        "code": chunk["content"],
        "calls": graph_result["calls"],
        "called_by": graph_result["callers"]
    }
@app.get("/graph")
def get_graph():
    from neo4j import GraphDatabase

    URI = "neo4j://127.0.0.1:7687"
    USER = "neo4j"
    PASSWORD = "12345678"

    driver = GraphDatabase.driver(
        URI,
        auth=(USER, PASSWORD)
    )

    with driver.session() as session:
        result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN
                a.name AS source,
                labels(a)[0] AS source_type,
                type(r) AS relationship,
                b.name AS target,
                labels(b)[0] AS target_type
        """)

        relationships = []

        for record in result:
            relationships.append({
                "source": record["source"],
                "source_type": record["source_type"],
                "relationship": record["relationship"],
                "target": record["target"],
                "target_type": record["target_type"]
            })

    driver.close()

    return {
        "relationships": relationships
    }