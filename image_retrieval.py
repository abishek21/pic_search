from model import ClipModel
from qdrant_client import QdrantClient


# clip=ClipModel()
# client = QdrantClient("localhost", port=6333)
# embedding_size= 512
# collection_name = 'Apparel_collection'

def get_similar_images(client,collection_name,query_text_feature,k):
    search_result = client.search(collection_name=collection_name, query_vector=query_text_feature,
                                  with_payload=True,
                                  limit=k)

    search_result = process_search_results(search_result)

    return search_result

def process_search_results(search_results):
    similar_images = {'candidates':[],'scores':[]}
    for result in search_results:
        similar_images['scores'].append(result.score)
        similar_images['candidates'].append(result.payload['file_name'])

    return similar_images



def search_images(qdrant_client_params,collection_name,query_text,k=5):
    clip = ClipModel()
    client = QdrantClient(**qdrant_client_params)

    query_text_tokenized = clip.tokenize_text(query_text)
    query_text_feature = clip.text_embeddings(query_text_tokenized)

    search_results = get_similar_images(client,collection_name,query_text_feature,k)

    return search_results


# print(search_images('black shirt'))