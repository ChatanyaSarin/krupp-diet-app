from langchain.llms import LlamaCpp

def get_llm():
    return LlamaCpp(
        model_path="/path/to/model.gguf",
        temperature=0.7,
        max_tokens=2048,
        n_ctx=2048
    )