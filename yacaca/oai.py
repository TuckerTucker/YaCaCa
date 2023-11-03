import openai

def oai_init():
    with open(".OAI_KEY", "r") as f:
        openai.api_key = f.read().strip()

def getEmbedding(context_prompt):
    embedResponse = openai.Embedding.create(
        input = context_prompt,
        model = "text-embedding-ada-002",
    )
    contextEmbedding = embedResponse["data"][0]["embedding"]
    return contextEmbedding