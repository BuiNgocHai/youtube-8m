# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

# linear algebra
import numpy as np 

# data processing, CSV file I/O (e.g. pd.read_csv)
import pandas as pd 
import csv


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
        e = sys.exc_info()
        print(e)
        print('False in ' + url)
    return check


def get_video(total_csv, total_write):
    for i in range(len(total_csv)):
        csv_path = total_csv[i]
        path_write = total_write[i]

        name_csv = csv_path[-13:]
        if not os.path.isdir(path_write):
            os.mkdir(path_write)
            with open(path_write+'/'+name_csv, mode = 'w') as output_file:
                count = 0
                for video_file, labels in csv.reader(open(csv_path)):
                    print(name_csv)
                    try:
                        check = get_metadata(video_file,path_write+'/')
                    except:
                        e = sys.exc_info()
                        print(e)
                    if check == True:
                        write_data = []
                        write_data.append(video_file)
                        write_data.append(labels)
                        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        writer.writerow(write_data)  
                if count < 200:
                    os.removedirs(path_write)
                    raise IOError('Dowload unsucess')

            with open('/storage1/haibn/yt8m/2/check_done/'+name_csv, mode = 'w') as done_file:
                log = []
                log.append('done')
                writer = csv.writer(done_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(log)  


def main():
    path = "/storage1/haibn/yt8m/2/csv/"
    path_write = '/storage1/haibn/yt8m/2/video/'
    file_csv = []
    file_write = []
    total_csv = []
    total_write = []
    count = 0
    for file_name in os.listdir(path):
        file_csv.append(path+file_name+'/'+file_name+'.csv')
        file_write.append(path_write+file_name)
        count +=1
        if count == 15:
            total_csv.append(file_csv)
            total_write.append(file_write)
            file_csv = []
            file_write = []
            count = 0
    if count!=0:
        total_csv.append(file_csv)
        total_write.append(file_write)

    for i in range(len(total_csv)):
        thread = threading.Thread(target=get_video, args=(total_csv[i],total_write[i], ))
        thread.start()
        print('Thread loaded: ' ,i)

if __name__ == "__main__":
    main()

