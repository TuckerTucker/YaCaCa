import tiktoken
import streamlit as st

def num_tokens_from_messages(messages, model = "gpt-3.5-turbo"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        st.warning("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens_per_message = 3 
    tokens_per_name = 1 

    num_tokens = 0
    for message in messages:
        num_tokens +=  tokens_per_message
        for key, value in message.items():
            # Ensure value is a string before encoding
            if isinstance(value, str):
                num_tokens +=  len(encoding.encode(value))
            if key ==  "name":
                num_tokens +=  tokens_per_name

    num_tokens +=  3  # every reply is primed with assistant
    return num_tokens