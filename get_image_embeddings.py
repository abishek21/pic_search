import torch
import clip
from PIL import Image
import os
import numpy as np
from annoy import AnnoyIndex
from tqdm import tqdm
import json
from numpyencoder import NumpyEncoder

image_dir_boys = '/home/frank/Desktop/pic_search/data/ecommerce/Apparel/all_apparels/'
image_files = list(os.listdir(image_dir_boys))



print(len(image_files))
embedding_size=512
clip_embedding = {}

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def normalize_vector(vector):
    return vector/np.linalg.norm(vector)

def clip_preprocess_image(image_path):
    return preprocess(Image.open(image_path)).unsqueeze(0).to(device)

def clip_image_embeddings(image):
    with torch.no_grad():
        image_features = model.encode_image(image)

    image_features = np.array(image_features.cpu())
    image_features = np.reshape(image_features,(embedding_size,))
    image_features = normalize_vector(image_features)
    return image_features

def save_dict(d,out_dir,filename,cls=None):
    with open(out_dir+filename, 'w') as f:
        json.dump(d, f,cls=cls)



for image_path in tqdm(image_files):
    image_clip=clip_preprocess_image(image_dir_boys+image_path)
    image_features = clip_image_embeddings(image_clip)
    clip_embedding[image_path]=image_features



save_dict(clip_embedding,'./','clip_embedding_apparels.json',cls=NumpyEncoder)

index = AnnoyIndex(embedding_size, 'dot')



for key,value in clip_embedding.items():
    value = value.astype('float32')
    id = int(key.split('.')[0])
    index.add_item(id, value)

index.build(1000)
print('[INFO] index built')
#
index.save('clip_embeddings.ann')
print('[INFO] index saved')








