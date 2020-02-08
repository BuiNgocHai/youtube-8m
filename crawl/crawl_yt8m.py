# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

# linear algebra
import numpy as np 

# data processing, CSV file I/O (e.g. pd.read_csv)
import pandas as pd 
import csv
#Loading libraries & datasets
import tensorflow as tf

# Input data files should be available in the "/input/" directory.
import os
import sys

from urllib.request import urlopen
from pytube import Playlist, YouTube
from pytube.helpers import safe_filename
from threading import Thread
import threading
import subprocess
# Any results you write to the current directory are saved as output.


# This function collects the data provided by youtube-dl, such as rendition tables, number of views, etc.
def convert_wav(name):
    src = name
    output = name[:-5]+'.mp4'
    command = 'ffmpeg -i ' +src +' -strict -2 '+ output
    subprocess.call(command, shell=True)

def get_metadata(video_id: str,path) -> str or None:
    url = 'https://www.youtube.com/watch?v=' + video_id
    check = True
    try:
        print('dowload video: '+ url)
        YouTube(url).streams.first().download(path)
        yt = YouTube(url)
        name = (safe_filename(yt.title) +".mp4")
        if os.path.isfile(path + safe_filename(yt.title) +".webm"):
            print('Convert to mp4')
            os.rename(path + safe_filename(yt.title) +".webm", path+video_id+".webm")

            convert_wav(path + video_id +".webm")
        else:
            os.rename(path+name,path+video_id+".mp4")

    except:
        check = False
        print('False in ' + url)
        #continue
    return check

# For privacy reasons the video IDs in the dataset were provided with a codification. 
# Instructions and further information are available here:
#      https://research.google.com/youtube8m/video_id_conversion.html
def get_real_id(random_id: str) -> str:
    url = 'http://data.yt8m.org/2/j/i/{}/{}.js'.format(random_id[0:2], random_id)
    request = urlopen(url).read()
    real_id = request.decode()
    return real_id[real_id.find(',') + 2:real_id.find(')') - 1]


def get_video(video_lvl_record, path_write):
    # The path to the TensorFlow record
    
    print(video_lvl_record)

    vid_ids = []
    labels = []

    data = []
    wanted_data = ['format', 'quality']
    name_csv = video_lvl_record[-18:-9]
    path_write+='/'
    if not os.path.isdir(path_write):
        os.mkdir(path_write)
    with open(path_write+name_csv+'.csv', mode='w') as output_file:

        # Iterate the contents of the TensorFlow record
        for example in tf.python_io.tf_record_iterator(video_lvl_record):
            
            # A TensoFlow Example is a mostly-normalized data format for storing data for
            # training and inference.  It contains a key-value store (features); where
            # each key (string) maps to a Feature message (which is oneof packed BytesList,
            # FloatList, or Int64List). Features for this data set are:
            #     -id
            #     -labels
            #     -mean_audio
            #     -mean_rgb
            tf_example = tf.train.Example.FromString(example)
            
            # Once we have the structured data, we can extract the relevant features (id and labels)
            vid_ids.append(tf_example.features.feature['id'].bytes_list.value[0].decode(encoding='UTF-8'))
            pseudo_id = tf_example.features.feature['id'].bytes_list.value[0].decode(encoding='UTF-8')
            labels = tf_example.features.feature['labels'].int64_list.value
            audio = tf_example.features.feature['mean_rgb'].int64_list.value
            
            # The id provided from the TensoFlow example needs some processing in order to build a valid link to a 
            # YouTube video
            try:
                real_id = get_real_id(pseudo_id)

                # Get the youtube-dl valuable metadata
                check = get_metadata(real_id, path_write)
            except:
                e = sys.exc_info()
                
            # Collect the data in the dataframe
            if check == True:
                data.append([real_id, labels])
                write_data = []
                write_data.append(real_id)
                s = ''
                for i in range(len(labels)):
                    s += labels[i]
                    if i!=len(labels)-1:
                        s+=';'
                write_data.append(s)
                writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(write_data)  
            print('Done')

def main():
    path = "/storage/haibn/yt8m/2/frame/"

    path_write = '/storage1/haibn/yt8m/2/csv/'
    

    file_tf = []
    file_write = []

    for file_name in os.listdir(path):
        if file_name[:5] == 'train':
            file_tf.append(path+file_name)
            file_write.append(path_write+file_name[:-9])

    for i in range(len(file_tf)):
        thread = threading.Thread(target=get_video, args=(file_tf[i], file_write[i], ))
        thread.start()
        print('Thread done : ', i)

def main2():
    path = "/storage/haibn/yt8m/2/frame/"
    path_write = '/storage1/haibn/yt8m/2/csv/'
    get_video(path, path_write)
    
if __name__ == "__main__":
    main2()

