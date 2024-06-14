from app import app, cache
from utils.helper import move_to_static_folder
from flask import request, render_template, jsonify
import os
from image_retrieval import search_images
from flask import url_for


def get_collection_status(collection_name):
    return cache.get(f'{collection_name}_status')


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        if request.method == 'POST':
            query = request.form['query']
            collection_name = request.form.get('catalogName', '')
            # check if collection_name has completed building index
            if get_collection_status(collection_name):
                search_results = search_images(app.config['QDRANT_CLIENT_PARAMS'],collection_name,query)
                min_sim_score = search_results['scores'][0]
                # print(min_sim_score)
                if min_sim_score < 0.25:
                    return jsonify({"response": "No relevant images found"})

                images_to_show = search_results['candidates']
                image_path_dir = os.path.join(app.config['DATA_DIR'], collection_name,'images')
                move_to_static_folder('app/static',image_path_dir,images_to_show,query)
                image_urls = [url_for('static', filename=f'{query}/{image}') for image in images_to_show]



                return render_template('search.html', image_urls=image_urls,catalog_name=collection_name)

            else:
                return jsonify({"response": "Catalog is still building"})

        else:
            # Initial page load without POST data
            return render_template('search.html', image_urls=[],catalog_name='')
    except Exception as e:
        return str(e)