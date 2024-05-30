import numpy as np
import shutil
import os
import random
import string
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
import time
from flask_app import cache

def generate_random_id(length=8):
    # Generates a random string of letters and digits
    characters = string.digits
    random_id = ''.join(random.choice(characters) for i in range(length))
    return int(random_id)


def normalize_vector(vector):
    return vector/np.linalg.norm(vector)


def move_to_static_folder(dest,source_dir,files,folder_name_with_query):
    os.makedirs(os.path.join(dest,folder_name_with_query),exist_ok=True)
    for f in files:
        shutil.copy(os.path.join(source_dir,f),os.path.join(dest,folder_name_with_query))


def valid_csv(csv_fp):
    df=pd.read_csv(csv_fp)

    if len(df)>0 and 'image url' in df.columns:
        image_urls = df['image url'].tolist()
        return True,image_urls
    else:
        return False,[]


def download_images(data_dir,url):
    #url = 'https://s3.eu-west-1.amazonaws.com/s3.logograb.com/pub/rendered-media/{}/frames/{}.jpg'.format(sessionID,str(frame))
    #print(url)
    r=requests.get(url)
    if r.status_code== 200:
        data = requests.get(url).content
        filename=url.split('/')[-1]

        # gt=gt_label[int(filename.split('.')[0])]
        fp_file_dest=data_dir+'/'+filename
        with open(fp_file_dest, 'wb') as handler:
            handler.write(data)
    else:
        print(f'[INFO] {url} failed {r.status_code}')


def download_images_concurrently(data_dir, urls, max_workers=5):


    # Ensure the directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Use ThreadPoolExecutor to download images concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map each URL to the download_image function
        futures = [executor.submit(download_images, data_dir, url) for url in urls]

        # Optionally, you can wait for all futures to complete and handle exceptions
        for future in futures:
            try:
                # Result method would raise any exceptions that occurred during execution
                future.result()
            except Exception as e:
                print(f"Error occurred: {e}")



def download_images_from_folder(file,collection_name,DATA_DIR):

    if file.filename == '':
        return 'No selected files'
    if file:
        filename = file.filename
        filename = filename.split('/')[-1]
        file.save(os.path.join(DATA_DIR,filename))


def download_images_from_folder_concurrently(files,collection_name,DATA_DIR,max_workers=5):
    # Ensure the directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Use ThreadPoolExecutor to download images concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map each URL to the download_image function
        futures = [executor.submit(download_images_from_folder,f,collection_name, DATA_DIR) for f in files]

        # Optionally, you can wait for all futures to complete and handle exceptions
        for future in futures:
            try:
                # Result method would raise any exceptions that occurred during execution
                future.result()
            except Exception as e:
                print(f"Error occurred: {e}")






def update_collection_status(collection_nname,status):
    from app import cache
    cache.set(f'{collection_nname}_status', status, timeout=0)

def get_collection_status(collection_nname):
    from app import cache
    return cache.get(f'{collection_nname}_status')




def get_csv_fp(collection_dir):
    # List all files in the directory
    files = os.listdir(collection_dir)

    # Find the CSV file
    csv_file = None
    for file in files:
        if file.endswith('.csv'):
            csv_file = file
            break

    if csv_file:
        # Construct the full path to the CSV file
        csv_file_path = os.path.join(collection_dir, csv_file)

        return csv_file_path



def get_image_url(search_result,csv_file_path):
    import pandas as pd
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    search_result_url={'candidates':[],'scores':[]}
    for candidate,score in zip(search_result['candidates'],search_result['scores']):
        filename=candidate.split('?')[0]
        imageurl = df[df['image_name'] == filename]['image url'].values[0]
        search_result_url['candidates'].append(imageurl)
        search_result_url['scores'].append(score)

    return search_result_url

