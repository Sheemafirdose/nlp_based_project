import ollama

def get_code_suggestions(code):
    prompt = f"Review the following Python code for a Streamlit NLP app and suggest improvements:\n\n```python\n{code}\n```"

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']
