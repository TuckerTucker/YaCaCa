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
parser = argparse.ArgumentParser(description = "Load chat history.")
parser.add_argument("--load_chat", type = str, help = "File to load chat history from.")
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

# Check session state
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
    # create max_tokens varibale from session 
    max_tokens = st.session_state.ai_settings["max_tokens"]
    # add the user prompt to the messages list
    st.session_state.messages.append({"role": "user", "content": prompt})
    #show the prompt in the chat window
    ui_messages([{"role": "user", "content": prompt}])

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
# Calculate the tokens.
    tokens_so_far = 0
    last_index = 0
    
    for i, message in enumerate(reversed(st.session_state.messages)):
        tokens = num_tokens_from_messages([message], model = st.session_state.ai_settings["model"])
        if tokens_so_far + tokens > max_tokens:
            break
        tokens_so_far +=  tokens
        last_index = len(st.session_state.messages) - 1 - i
    
    # Store the last_index for use truncating prompt messages
    st.session_state.prompt_end_index = last_index

    # set the long convo msg
    model = st.session_state.ai_settings["model"]
    theContext = max_tokens
    skipped = last_index + 1  
    st.session_state.long_convo_msg = f"> ✂️&nbsp;&nbsp;The first **{skipped}** messages are no longer seen by the AI. The chat has grown beyond the context window for this model ({model} — {max_tokens} tokens)."

    # the most recent messages that fit within the available context window
    oai_messages = [
        {"role": "system", "content": st.session_state.prompts.get("system_prompt")},
        * [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[last_index + 1:]]
    ]
    
    # Add the user's prompt to oai_messages
    oai_messages.append({"role": "user", "content": prompt})

    full_response = ""
    # call openai to get the response
    for response in openai.chat.completions.create(
        model = st.session_state.ai_settings["model"],
        messages = oai_messages,
        max_tokens = 1024,
        stream = True,
    ): # Check for None before concactenating
        if response.choices[0].delta.content is not None:
            # Extract the content from the response
            content = response.choices[0].delta.content
        else:
            content = ""   

        # Append the content to the full response
        full_response += content
        # Display the response as it streams in
        message_placeholder.markdown(full_response + "▌")

        # Check the finish_reason
        finish_reason = response.choices[0].finish_reason
        if finish_reason == 'stop':
            # If the finish_reason is 'stop', break the loop
            break
        elif finish_reason == 'length':
            # If the finish_reason is 'length', display a message to the user
            st.warning("The response was cut-off due to length.")

    # Add the full response to the full messages list
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Update chat history
    update_chat_history_to_file(st.session_state.filename, st.session_state.messages)

# The Convo Is Too Long message
# if all(key in st.session_state for key in ["long_convo_msg"]):
#    st.markdown(st.session_state.long_convo_msg)