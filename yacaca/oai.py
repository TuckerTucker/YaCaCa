import openai

def oai_init():
    with open(".OAI_KEY", "r") as f:
        openai.api_key = f.read().strip()