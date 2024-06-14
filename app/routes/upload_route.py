from app import app, cache,q
from utils.helper import valid_csv,download_images_concurrently,download_images_from_folder_concurrently
from flask import request, render_template,jsonify
import os
from upload_image_embeddings import upload_image_embeddings
from utils.qdrant_utils import create_collection
from werkzeug.utils import secure_filename


def create_image_dir(DATA_DIR,collection_name):
    # Ensure the upload folder exists
    os.makedirs(os.path.join(DATA_DIR,collection_name), exist_ok=True)

def update_collection_status(collection_name,status):
    cache.set(f'{collection_name}_status', status, timeout=0)
    print(f'cache for {collection_name}_status set : {status}')



@app.route('/upload_assets', methods=['POST'])
def upload_folder():
    try:
        collection_name = request.form.get('catalogName')
        collection_name = str(collection_name)
        update_collection_status(collection_name,False)


        create_collection(app.config['QDRANT_CLIENT_PARAMS'],collection_name,app.config['EMBEDDING_SIZE'])
        create_image_dir(app.config['DATA_DIR'],collection_name)

        upload_type=request.form.get('uploadType')
        if upload_type=='Folder':
            files = request.files.getlist('files[]')  # Get the list of files from the form
            image_path_dir = os.path.join(app.config['DATA_DIR'], collection_name,'images')

            # DATA_DIR = app.config['DATA_DIR']

            download_images_from_folder_concurrently(files,collection_name,image_path_dir)

            # TODO serialize files and put into queue
            # image_download_jobs = q.enqueue(download_images_from_folder_concurrently, args=(files,collection_name,DATA_DIR))

            # async_image_embeddings(clip,client,image_path_dir,collection_name)

            upload_image_embeddings_job = q.enqueue(upload_image_embeddings,
                                                    args=(app.config['QDRANT_CLIENT_PARAMS'], image_path_dir, collection_name),
                                                    # depends_on=image_download_jobs
                                                    )

        elif upload_type=='csv':
            # Process uploaded CSV file
            csv_file = request.files['csvFile']
            if csv_file:
                if not csv_file.filename.endswith('.csv'):
                    return jsonify({"error": "File is not a CSV"}), 400

                filename = secure_filename(csv_file.filename)

                # Ensure the file is a CSV
                collection_dir = os.path.join(app.config['DATA_DIR'], collection_name)
                os.makedirs(collection_dir, exist_ok=True)

                file_path = os.path.join(collection_dir, filename)
                csv_file.save(file_path)

                csv_status, image_urls = valid_csv(file_path)
                ### download image urls
                image_dir = os.path.join(collection_dir, 'images')
                os.makedirs(image_dir, exist_ok=True)

                ## put jobs on queue to download images
                image_download_jobs = q.enqueue(download_images_concurrently,
                                                args=(image_dir, image_urls),job_timeout=1200)

                upload_image_embeddings_job = q.enqueue(upload_image_embeddings,
                                                        args=(app.config['QDRANT_CLIENT_PARAMS'], image_dir, collection_name),job_timeout=60*60,
                                                        depends_on=image_download_jobs
                                                        )


                update_status_job = q.enqueue(update_collection_status,
                                              args=(collection_name,True),
                                              depends_on=upload_image_embeddings_job)
                # download_images_concurrently(image_dir, image_urls)
                # upload_image_embeddings(clip, client, image_dir, collection_name)

                if csv_status:
                    return jsonify({"status": "Success"}), 200
                else:
                    return jsonify({"error": "The csv file is not in the require format"}), 422

            else:
                return jsonify({"error": "The csv file is not in the require format"}), 422

        # upload_image_embeddings(clip,client,image_path_dir,collection_name)



        return render_template('search.html', image_urls=[],catalog_name='')
    except Exception as e:
        return jsonify({'error':e})