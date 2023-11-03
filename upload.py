import streamlit as st
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from yacaca.oai import oai_init, getEmbedding
from yacaca.qdrant import qdrantConnection, makeQdrantPointsList

def main():
    # Streamlit Interface
    st.title('Document Upload to Qdrant Collection')

    # Collection Inputs
    collection_name = st.text_input("Enter Collection Name")
    vector_dim = st.number_input("Enter Vector Dimension", min_value=0, value=1536)

    # Text Inputs
    document_text = st.text_area("Enter the document text")
    
    # Submit Button
    submit = st.button("Submit")

    if submit:
        try:
            # Load the qdrant API Key
            with open(".qdrant_key", "r") as f:
                qdrantApiKey = f.read().strip()

            client = create_qdrant_client()
            recreate_collection(client, collection_name, vector_dim)
            st.success(f'Successfully created collection: {collection_name}')

            # Load the Qdrant Host
            with open("chats/convo_vdb", 'r') as f:  
                data = json.load(f)
                qdrantHost = data["qdrant"]["cluster_url"]
                
            # Initialize OpenAI
            oai_init()

            # Get the Context Embedding
            contextEmbedding = getEmbedding(document_text)

            if contextEmbedding is not None:
                # Upsert the Embedding to Qdrant
                qdrant_connect = qdrantConnection(qdrantApiKey, qdrantHost)
                theData = [(contextEmbedding, {"text": document_text})]
                makeQdrantPointsList(qdrant_connect, theData, collection_name)
                st.success('Document added to collection successfully!')
        except Exception as e:
            st.error("An error occurred: {}".format(str(e)))

def create_qdrant_client():
    cluster_url = get_cluster_url()
    with open('.qdrant_key', 'r') as f:
        api_key = f.read().strip()
    qdrant_client = QdrantClient(
        host=cluster_url,  
        prefer_grpc=True,  
        api_key=str(api_key),  
    )
    return qdrant_client

def get_cluster_url():
    convo_file = "chats/convo_vdb"
    _, _, _, qdrant = load_chat_history_from_file(convo_file)
    return qdrant['cluster_url']

def recreate_collection(client, collection_name, vector_dim):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_dim,
            distance=Distance.COSINE,
        ),
    )

def load_chat_history_from_file(filename):
    with open(filename, "r") as f:
        data = json.loads(f.read())
        return data["conversation"], data["prompts"], data["ai_settings"], data["qdrant"]

if __name__ == '__main__':
    main()