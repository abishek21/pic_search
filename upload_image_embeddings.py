from model import ClipModel
import os
from qdrant_client import QdrantClient
from tqdm import tqdm
from utils.qdrant_utils import create_collection,add_embeddings_to_collection,make_points_struct,collection_exists
from qdrant_client import QdrantClient

# clip=ClipModel()
# client = QdrantClient("localhost", port=6333)
# embedding_size= 512
#
# collection_name = 'Apparel_collection'
#
# if collection_exists(client,collection_name):
#     print(f'[INFO] {collection_name} already exists')
# else:
#     create_collection(client,collection_name,embedding_size)

def upload_image_embeddings(qdrant_client_params,image_dir,collection_name):
    clip = ClipModel()
    client = QdrantClient(**qdrant_client_params)

    image_files = list(os.listdir(image_dir))
    clip_embedding={}
    for image_path in tqdm(image_files):
        image_clip = clip.preprocess_image(os.path.join(image_dir, image_path))
        image_features = clip.image_embeddings(image_clip)
        clip_embedding[image_path] = image_features

    points=make_points_struct(clip_embedding)
    add_embeddings_to_collection(client,collection_name,points)
    print(f'[INFO] {len(image_files)} image embeddings added to qdrant')



# upload_image_embeddings('/home/frank/Desktop/pic_search/data/ecommerce/Apparel/all_apparels/',collection_name)