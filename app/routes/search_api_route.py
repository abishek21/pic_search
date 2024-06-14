from app import app, cache
from utils.helper import get_csv_fp,get_image_url
from flask import request,jsonify
import os
from image_retrieval import search_images


def get_collection_status(collection_name):
    return cache.get(f'{collection_name}_status')


@app.route('/api/visual_search', methods=['GET'])
def visual_search():
    try:
        if request.method == 'GET':
            query = request.args.get('query')
            collection_name = request.args.get('catalogName', '')
            if get_collection_status(collection_name):
                search_results = search_images(app.config['QDRANT_CLIENT_PARAMS'],collection_name,query)
                collection_dir = os.path.join(app.config['DATA_DIR'], collection_name)
                csv_fp=get_csv_fp(collection_dir)
                if os.path.exists(csv_fp):
                    search_results_url=get_image_url(search_results,csv_fp)
                    return jsonify(search_results_url),200
            else:
                return jsonify({"response": "Catalog is still building"})

    except Exception as e:
        return str(e)