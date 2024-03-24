import numpy as np
import shutil
import os
import random
import string
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
import time

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
    df=pd.read_csv(csv_fp,header=None)
    if len(df)>0:
        return True,df[1:][0].tolist()
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
        print(r.status_code)


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
