import pymysql
import sys
import zlib

import json
from time import sleep

from kafka import KafkaConsumer, KafkaProducer, TopicPartition
import ast
from threading import Thread
import threading
import wget
import subprocess
import csv
import os
import shutil
import pandas as pd
import time
from bson import json_util

path = '/storage1/haibn/data_kafka/'
def dowload_video(url, post_id, id_video):
    if not os.path.isdir(path + post_id + '/'):
        os.mkdir(path+post_id + '/')
    else:
        shutil.rmtree(path+post_id + '/')
        os.mkdir(path+post_id + '/')
    name = id_video
    try:
        name_csv = name + '.csv'
        name_video = name + '.mp4'

        print('Dowload video: ' + url)

        wget.download(url, path + post_id + '/' + name_video)
        #save in csv
        with open(path + post_id + '/' + name_csv, mode = 'w') as output_file:
            for file_name in os.listdir(path + post_id):
                if (file_name[-4:] == '.mp4'):
                    writer = csv.writer(output_file, delimiter =',', quotechar ='"', quoting = csv.QUOTE_MINIMAL)
                    writer.writerow([path + post_id + '/'+file_name, '342'])
    except:
        print('Dowload fail ' + url)
    
def video_class(post_id, id_video):
    path_csv = path + post_id + '/' + id_video+'.csv'
    path_tfrecord = path + post_id + '/' + id_video+'.tfrecord'
    command_extract = 'python3 /storage/haibn/yt8m/code/video_classification/feature_extractor/extract_tfrecords_main.py --input_videos_csv=' + path_csv + ' --output_tfrecords_file=' + path_tfrecord + ' --extract_wav=False'
    subprocess.call(command_extract, shell=True)
    path_csv_infer = path + post_id + '/' + id_video+'_res.csv'
    command_inference = 'python3 /storage/haibn/yt8m/code/video_classification/inference.py --train_dir=/storage/haibn/yt8m/2/models/frame/model_only_frame/ --output_file=' + path_csv_infer +' --input_data_pattern='+path_tfrecord
    subprocess.call(command_inference, shell=True)

def convert_label(post_id, id_video, url):
    #read_csv
    data = pd.read_csv(path + post_id +'/' +id_video + '_res.csv')
    labels = pd.read_csv('label_names.csv')
    labels_lotus = pd.read_csv('lotus_label.csv')
    label_db = []

    total = data['VideoId']
    data_final = {}

    for index in range(len(total)):
        print(index)
        name_of_video = id_video +'.mp4'
        link = url
        _class = data['LabelConfidencePairs'][index].split()
        label = []
        if (float(_class[1]) > 0.1):
            label_db.append(labels_lotus.label_name[labels_lotus.label_id[labels_lotus.label_id == int(_class[0])].index[0]])
        else:
            label_db.append('30000')
        for i in range(len(_class)):

            if i%2 == 0:
                #print(_class[i])
                label.append(labels.label_name[labels.label_id[labels.label_id == int(_class[i])].index[0]] + ': ' + _class[i+1]) 
        data_final[index] = []
        data_final[index].append({
            'name' : name_of_video,
            'link' : link,
            'class': label
            
        }) 
    return data_final,label_db

def convert_crc32(name):
    name = bytes(name, 'utf-8')
    prev = zlib.crc32(name, 0)
    return prev
def convert(results):
    count = 0
    for item in results:
        
        start_time = time.time()
        post_id = str(item[0])
        data_final = []
        url_mysql = []
        url = str(item[1])
        if url[-12:] == '/master.m3u8':
            url = url[:-12]
        url_mysql.append(url)
        id_video = str(item[0])

        print('Id ' + ' : ' + id_video )
        print('Url ' + ' : ' + url )
        #name = post_id + '_' + id_vieo
        dowload_video(url, post_id, id_video)
        print('Start classification')
        video_class(post_id, id_video)
        #Convert to label
        file_name = path + post_id + '/' +id_video+'_res.csv'
        if os.path.isfile(file_name):
            data,label_db = convert_label(post_id, id_video, url)
            print(data)
            data_final.append(data)

            #send data

        print('Time end kafka: ', time.time()- start_time)
        print('----------------------------------------------------------------')
        try :
            #POST to mysql
            #connect to mysql
            db = pymysql.connect("172.26.6.30",'video_classification',password = 'J83YWZbNgGpPycm5Y3Fu')
            cursor = db.cursor()
            #check primary key exits:
            check_pri_cmd = "SELECT EXISTS( \
                SELECT * \
                    FROM kinghub.post_category \
                        where post_id = " + post_id + ' )'
            cursor.execute(check_pri_cmd)
            check = cursor.fetchall()

            if check[0][0] == 0:
                #INsert
                insert_cmd = 'INSERT INTO kinghub.post_category(`post_id`,`card_type`,`link`, `link_crc32`, `video_cate_3`) \
                    VALUES( %d,%d,%s,%d,%d )'
                link_crc32 = convert_crc32(url_mysql[0])
                args = (int(post_id),3,url_mysql[0],int(link_crc32), int(label_db[0]))
                cursor.execute(insert_cmd, args)
                db.commit()
            else:
                update_cmd = 'UPDATE kinghub.post_category \
                    SET video_cate_3 = ' + label_db[0] +' \
                        WHERE post_id = ' + post_id + ' && link_crc32 = ' + str(convert_crc32(url_mysql[0]))
                cursor.execute(update_cmd)
                db.commit()
        except:
            e = sys.exc_info()
            print(e)
        count +=1 
        print('preict file :{}. total:{}',count,len(results) )

if __name__ == '__main__':

    db = pymysql.connect("172.26.6.30",'video_classification',password = 'J83YWZbNgGpPycm5Y3Fu')
    sql = "select post_id,link,video_cate_1,video_cate_3 from kinghub.post_category \
    where video_cate_1 is not null && video_cate_3 is null"
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    
    total_data = []
    data = []
    print('found missing: ' + str(len(results)))

    num_data_thread = int(len(results)/100)
    index = 0
    for i in range(len(results)):

        data.append(results[i])
        if i == num_data_thread:
            total_data.append(data)
            data = []
    if len(data) != 0 :
        total_data.append(data)

    for index in range(len(total_data)):
        thread = threading.Thread(target=convert, args=(total_data[index], ))
        thread.start()
        print('Thread done : ', index)


