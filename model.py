import clip
import torch
from PIL import Image
import numpy as np
from utils.helper import normalize_vector

class ClipModel:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load('ViT-B/32', device=self.device)
        self.embedding_size = 512

    def preprocess_image(self, image_path):
        """Preprocess the image for CLIP model"""
        image = Image.open(image_path)
        return self.preprocess(image).unsqueeze(0).to(self.device)

    def image_embeddings(self, image_tensor):
        """Get image embeddings from the CLIP model"""
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)

        image_features = np.array(image_features.cpu())
        image_features = np.reshape(image_features, (self.embedding_size,))
        image_features = normalize_vector(image_features)
        return image_features

    def tokenize_text(self,query_text):
        query_text_tokenized = clip.tokenize([query_text]).to(self.device)
        return query_text_tokenized

    def text_embeddings(self,query_text_tokenized):
        with torch.no_grad():
            text_features = self.model.encode_text(query_text_tokenized)

        text_features = np.array(text_features.cpu())
        text_features = np.reshape(text_features, (self.embedding_size,))
        text_features = normalize_vector(text_features)
        return text_features

# Example usage
# if __name__ == '__main__':
#     clip_model = ClipModel()
#
#     # Replace 'path_to_your_image.jpg' with the path to the image you want to process
#     image_path = 'path_to_your_image.jpg'
#     preprocessed_image = clip_model.clip_preprocess_image(image_path)
#     embeddings = clip_model.clip_image_embeddings(preprocessed_image)
#     print(embeddings)
