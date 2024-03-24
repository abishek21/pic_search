from annoy import AnnoyIndex
import clip
import torch
import numpy as np


device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

filepath = 'clip_embeddings.ann'



embedding_size= 512

def normalize_vector(vector):
    return vector/np.linalg.norm(vector)

def load_annoy_index(filepath,embedding_size):
    index = AnnoyIndex(embedding_size, 'dot')
    index.load(filepath)

    return index

index=load_annoy_index(filepath,embedding_size)
print('[info] index loaded')

def tokenize_text(query_text):
    query_text_tokenized = clip.tokenize([query_text]).to(device)
    return query_text_tokenized

def get_text_features(query_text_tokenized):

    with torch.no_grad():
        text_features = model.encode_text(query_text_tokenized)

    text_features = np.array(text_features.cpu())
    text_features = np.reshape(text_features,(embedding_size,))
    text_features = normalize_vector(text_features)
    return text_features

def search_images(query_text):
    query_text_tokenized = tokenize_text(query_text)
    query_text_feature = get_text_features(query_text_tokenized)

    candidates, scores = index.get_nns_by_vector(query_text_feature.tolist(), 5, include_distances=True)

    return candidates,scores



#
#
# similar_images,similarity_scores=search_images('black t shirt')
# print(similar_images)
# print(similarity_scores)
#
#
# similar_images,similarity_scores=search_images('black  shirt')
# print(similar_images)
# print(similarity_scores)
#










