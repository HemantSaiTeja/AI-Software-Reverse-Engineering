import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:8b"


def ask_llm(question, code, calls, called_by):
    prompt = f"""
/no_think

You are an AI software reverse-engineering assistant.

Answer the user's question using ONLY the provided project context.

User Question:
{question}

Relevant Code:
{code}

Functions or methods called by this code:
{calls}

Functions or methods that call this code:
{called_by}

Give a short and direct answer in 2-4 sentences.

Mention the relevant function or method and file when appropriate.

Do not invent information.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 120
            }
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    return result["response"]