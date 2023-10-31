# Python Imports
import argparse
import json
import streamlit as st
import openai
from datetime import datetime

# Local Imports
from yacaca.token_counter import num_tokens_from_messages
from yacaca.file_io import load_default_chat, load_chat_history_from_file, update_chat_history_to_file
from yacaca.oai import oai_init
from yacaca.ui_messages import ui_messages

# Parse the CLI arguments
parser = argparse.ArgumentParser(description="Load chat history.")
parser.add_argument("--load_chat", type=str, help="File to load chat history from.")
args = parser.parse_args()

# Initialize OpenAI
oai_init()

# Initialize chat history and filename
def load_default_to_session_state():
    default_conversation = load_default_chat()
    st.session_state.messages = default_conversation["messages"]
    st.session_state.prompts = default_conversation["prompts"]
    st.session_state.filename = default_conversation["filename"]
    st.session_state.ai_settings = default_conversation["ai_settings"]

# Check session_state - Load Existing? Load Default?
if not all(key in st.session_state for key in ["messages", "prompts", "filename"]):
    if args.load_chat:
        try:
            st.session_state.messages, st.session_state.prompts, st.session_state.ai_settings = load_chat_history_from_file(args.load_chat)
            st.session_state.filename = args.load_chat
        except FileNotFoundError:
            st.warning(f"Could not find file {args.load_chat}. Initializing with default message.")
            load_default_to_session_state()
    else:
        load_default_to_session_state()

# Display chat history
ui_messages(st.session_state.messages)

# Accept user input
if prompt := st.chat_input(st.session_state.prompts.get("default_prompt")):
    MAX_TOKENS = st.session_state.ai_settings["max_tokens"]
    st.session_state.messages.append({"role": "user", "content": prompt})
    ui_messages([{"role": "user", "content": prompt}])

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

    total_tokens = num_tokens_from_messages(st.session_state.messages + [{
        "role": "user",
        "content": prompt
    }])

    if total_tokens > MAX_TOKENS:
        st.toast('The conversation has gotten quite long. Some early messages are no longer used as part of the prompt.', icon='✂️')
        while total_tokens > MAX_TOKENS:
            st.session_state.messages.pop(0)
            total_tokens = num_tokens_from_messages(st.session_state.messages + [{"role": "user", "content": prompt}])

    full_response = ""
    for response in openai.ChatCompletion.create(
        model=st.session_state.ai_settings["model"],
        messages=[
            {"role": "system", "content": st.session_state.prompts.get("system_prompt")},
            * [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        ],
        stream=True,
    ):
        full_response += response.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    update_chat_history_to_file(st.session_state.filename, st.session_state.messages)