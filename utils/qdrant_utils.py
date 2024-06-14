import json
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from utils.helper import generate_random_id
from qdrant_client import QdrantClient


def collection_exists(client,collection_name):
    collections = client.http.collections_api.get_collections().result.collections
    return any(collection.name == collection_name for collection in collections)

def create_collection(qdrant_client_params,collection_name,embedding_size):
    client = QdrantClient(**qdrant_client_params)
    if collection_exists(client, collection_name):
        print(f'[INFO] {collection_name} already exists')
    else:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_size, distance=Distance.COSINE),
        )
        print(f'[INFO] collection {collection_name} created ')


def make_points_struct(clip_embeddings):
    points=[]
    for key,value in clip_embeddings.items():
        id=generate_random_id()
        points.append(PointStruct(id=id, vector=value, payload={"file_name": key,"id":id}))

    return points

def add_embeddings_to_collection(client,collection_name,points):
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points,
    )

    print(operation_info)