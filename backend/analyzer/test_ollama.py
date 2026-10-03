import ollama

response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": "Explain Python functions in one sentence."
        }
    ]
)

print(response["message"]["content"])