import json
from datetime import datetime

# Load chat history and prompts
def load_chat_history_from_file(filename):
    filename = "./chats/" + filename
    with open(filename, "r") as f:
        data = json.loads(f.read())
        return data["conversation"], data["prompts"], data["ai_settings"]

def update_chat_history_to_file(filename, messages):
    # Load existing data
    filename = "./chats/" + filename
    with open(filename, "r") as f:
        data = json.loads(f.read())
    
    # Update conversation history
    for message in messages:
        message["date"] = datetime.now().strftime("%Y-%m-%d")
        message["time"] = datetime.now().strftime("%H:%M:%S.%f")
    data["conversation"] = messages
    
    # Write data back to file
    with open(filename, "w") as f:
        f.write(json.dumps(data))

def load_default_chat():
    # get default convo template
    filename = "./yacaca/convo_default"
    with open(filename, "r") as f:
        data = json.loads(f.read())
    
    # Generate a timestamp
    theTimestamp = datetime.now().strftime("%b%d_%I_%M_%S%p").lower()
    
    # save new chat file with the timestamp
    filename = f"convo_{theTimestamp}"
    with open("./chats/" + filename, "w") as f:
        f.write(json.dumps(data))

    return {"messages": data["conversation"], "prompts": data["prompts"], "filename": filename, "ai_settings": data["ai_settings"] }