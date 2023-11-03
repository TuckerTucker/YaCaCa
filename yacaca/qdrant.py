import qdrant_client
from qdrant_client.http import models
from qdrant_client import QdrantClient
from qdrant_openapi_client import models
from qdrant_client.http.models import Distance, VectorParams, OptimizersConfig
from qdrant_client.http.models import CreateCollection
from yacaca.helpers import create_id

# init qdrant_connect 
qdrant_connect = None

# create the connection
def qdrantConnection(qdrantApiKey, qdrantHost):
    global qdrant_connect
    if qdrant_connect is None:
        try:
            qdrant_connect = qdrant_client.QdrantClient(
                host = qdrantHost,
                prefer_grpc = True,
                api_key = qdrantApiKey,
            )
        except Exception as e:
            print("Failed to connect to Qdrant:", str(e))
            # Raise the exception so that the calling function is aware
            raise
    return qdrant_connect

# Search the database for similar docs
def findSimilar(contextEmbedding, theCollection, qdrantHost):
    with open(".qdrant_key", "r") as f:
        qdrantApiKey = f.read().strip()
    qdrant_connect = qdrantConnection(qdrantApiKey, qdrantHost)
    theContextTemp = qdrant_connect.search(
        # collection_name = theCollection,
        collection_name = "convo_vdb",
        search_params = models.SearchParams(
            hnsw_ef = 128,
            exact = False,
        ),
        query_vector = contextEmbedding,
        limit = 3,
    )
    
    contextList = [f"{key}: {value}" for item in theContextTemp if len(item.payload) !=  0 for key, value in item.payload.items()]
    theContext = " ".join(contextList).replace("\n", " ")
    return theContext

def makeQdrantPointsList(qdrant_connect, allData, theCollection): 
    points = [models.PointStruct(id=create_id(), vector=embedding, payload=payload) 
              for embedding, payload in allData]

    setEmbedding(qdrant_connect, theCollection, points)

def setEmbedding(qdrant_connect, theCollection, point_list):
    qdrant_connect.upsert(
        collection_name = theCollection,
        points = point_list,
    )