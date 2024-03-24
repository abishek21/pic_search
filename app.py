from flask import Flask, request, render_template, send_from_directory,jsonify
import os
from upload_image_embeddings import upload_image_embeddings
from utils.qdrant_utils import create_collection
from model import ClipModel
from qdrant_client import QdrantClient
from image_retrieval import search_images
from flask import url_for
from utils.helper import move_to_static_folder,valid_csv,download_images_concurrently,download_images_from_folder_concurrently
from werkzeug.utils import secure_filename
from threading import Thread
import redis
from rq import Queue


app = Flask(__name__)

r = redis.Redis()
q = Queue(connection=r)

DATA_DIR = '/home/frank/Desktop/pic_search_image_collections/'
app.config['DATA_DIR'] = DATA_DIR
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # 100 MB


def create_image_dir(DATA_DIR,collection_name):
    # Ensure the upload folder exists
    os.makedirs(os.path.join(DATA_DIR,collection_name), exist_ok=True)

# clip=ClipModel()
client = QdrantClient("localhost", port=6333)
qdrant_client_params = {'host':'localhost','port':6333}
embedding_size= 512



def async_image_download(image_dir, image_urls):
    # Wrapper function to call your process_logic in a separate thread
    Thread(target=download_images_concurrently, args=(image_dir, image_urls)).start()

async def async_image_embeddings(clip,client,image_path_dir,collection_name):
    # Wrapper function to call your process_logic in a separate thread
    Thread(target=upload_image_embeddings, args=(clip,client,image_path_dir,collection_name)).start()

@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large', 413

@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    collection_name = request.form.get('catalogName')
    app.config['collection_name'] = collection_name
    create_collection(client,collection_name,embedding_size)

    create_image_dir(app.config['DATA_DIR'],collection_name)


    files = request.files.getlist('files[]')  # Get the list of files from the form
    image_path_dir = os.path.join(app.config['DATA_DIR'], collection_name,'images')

    # DATA_DIR = app.config['DATA_DIR']

    download_images_from_folder_concurrently(files,collection_name,image_path_dir)

    # TODO serialize files and put into queue
    # image_download_jobs = q.enqueue(download_images_from_folder_concurrently, args=(files,collection_name,DATA_DIR))




    # async_image_embeddings(clip,client,image_path_dir,collection_name)

    upload_image_embeddings_job = q.enqueue(upload_image_embeddings,
                                            args=(qdrant_client_params, image_path_dir, collection_name),
                                            # depends_on=image_download_jobs
                                            )

    # upload_image_embeddings(clip,client,image_path_dir,collection_name)



    return render_template('search.html', image_urls=[],catalog_name='')


@app.route('/api/upload', methods=['POST'])
def upload_api():
    try:
        collection_name = request.form.get('catalogName')
        create_collection(client, collection_name, embedding_size)
        file_type = request.form.get('filetype')

        if not collection_name or not file_type:
            return jsonify({"error": "Missing catalog name or CSV file"}), 400


        app.config['collection_name'] = collection_name
        create_image_dir(app.config['DATA_DIR'], collection_name)

        if file_type=='csv':
            file = request.files.get('csvFile')

            # Ensure the file is a CSV
            if not file.filename.endswith('.csv'):
                return jsonify({"error": "File is not a CSV"}), 400

            filename = secure_filename(file.filename)
            collection_dir = os.path.join(app.config['DATA_DIR'], collection_name)
            os.makedirs(collection_dir, exist_ok=True)

            file_path = os.path.join(collection_dir, filename)
            file.save(file_path)

            ### check if csv file is valid
            csv_status,image_urls=valid_csv(file_path)


            ### download image urls
            image_dir = os.path.join(collection_dir, 'images')
            os.makedirs(image_dir,exist_ok=True)

            ## put jobs on queue to download images
            image_download_jobs = q.enqueue(download_images_concurrently,args=(image_dir, image_urls))

            upload_image_embeddings_job = q.enqueue(upload_image_embeddings, args=(qdrant_client_params, image_dir, collection_name),
                                                    depends_on=image_download_jobs
                                                    )
            # download_images_concurrently(image_dir, image_urls)
            # upload_image_embeddings(clip, client, image_dir, collection_name)

            if csv_status:
                return jsonify({"status": "Success"}), 200
        else:
            return jsonify({"error": "The csv file is not in the require format"}), 422

    except Exception as e:
        print(e)
        return jsonify({"error": "Server error"}), 422









    # elif file_type=='image_folder':
    #     files = request.files.getlist('image_folder')  # Get the list of files from the form
    #     for file in files:
    #         if file.filename == '':
    #             return 'No selected files'
    #         if file:
    #             filename = file.filename
    #             filename = filename.split('/')[-1]
    #             file.save(os.path.join(app.config['DATA_DIR'], collection_name, filename))
    #
    #
    #     image_path_dir = os.path.join(app.config['DATA_DIR'], collection_name)

    #
    # create_collection(client,collection_name,embedding_size)
    #
    #
    #
    #
    #
    #
    #
    # upload_image_embeddings(clip,client,image_path_dir,collection_name)





@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        if request.method == 'POST':
            query = request.form['query']
            collection_name = request.form.get('catalogName', '')
            search_results = search_images(qdrant_client_params,collection_name,query)
            images_to_show = search_results['candidates']
            image_path_dir = os.path.join(app.config['DATA_DIR'], collection_name,'images')
            move_to_static_folder('static',image_path_dir,images_to_show,query)
            image_urls = [url_for('static', filename=f'{query}/{image}') for image in images_to_show]

            print(image_urls)

            return render_template('search.html', image_urls=image_urls,catalog_name=collection_name)
        else:
            # Initial page load without POST data
            return render_template('search.html', image_urls=[],catalog_name='')
    except Exception as e:
        return str(e)



@app.route('/api/visual_search', methods=['GET'])
def visual_search():
    if request.method == 'GET':
        query = request.args.get('query')
        collection_name = request.args.get('catalogName', '')
        search_results = search_images(qdrant_client_params,collection_name,query)
        return jsonify(search_results),200
    #     images_to_show = search_results['candidates']
    #     image_path_dir = os.path.join(app.config['DATA_DIR'], collection_name)
    #     move_to_static_folder('static',image_path_dir,images_to_show,query)
    #     image_urls = [url_for('static', filename=f'{query}/{image}') for image in images_to_show]
    #
    #     print(image_urls)
    #
    #     return render_template('search.html', image_urls=image_urls,catalog_name=collection_name)
    # else:
    #     # Initial page load without POST data
    #     return render_template('search.html', image_urls=[],catalog_name='')



if __name__ == '__main__':
    app.run(debug=True)
