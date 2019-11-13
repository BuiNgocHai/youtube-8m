import numpy as np 
import pandas as pd
from shutil import copyfile
import os
import tensorflow as tf
import numpy as np
from IPython.display import YouTubeVideo

path_news = '/storage/haibn/yt8m/2/frame_news/'
path_overwrite = '/storage/haibn/yt8m/2/frame/'
def write_train_old(name):
    b = tf.python_io.tf_record_iterator(name)
    for b_str in b:
        b = tf.python_io.tf_record_iterator(name)
        b_ex = tf.train.SequenceExample()
        b_ex.ParseFromString(b_str)
        #print(b_ex)
        writer.write(b_ex.SerializeToString())


train_name_file = []
for file_name in os.listdir(path_overwrite):
    if file_name[:5] == 'train':
        train_name_file.append(file_name)

print('Find ', str(len(train_name_file)) + ' File')

index = 0
writer = tf.io.TFRecordWriter('/storage/haibn/yt8m/2/data_suffer/' + train_name_file[index])

for file_name in os.listdir(path_news):
    record_iterator = tf.python_io.tf_record_iterator(path_news+file_name)
    check = False
    count = 0
    for string_record in record_iterator:
        example = tf.train.SequenceExample()
        example.ParseFromString(string_record)        
        count +=1

        writer.write(example.SerializeToString())

        if check == False:
            write_train_old(path_overwrite + train_name_file[index])
            print(path_overwrite + train_name_file[index])
            check = True
        if count == 12:
            index +=1
            count = 0
            check = False
            writer = tf.io.TFRecordWriter('/storage/haibn/yt8m/2/data_suffer/' + train_name_file[index])
    print('Done ',file_name)
    #break
if index < len(train_name_file) -1 :
    print('Copy ', str(len(train_name_file)) + 'File')
    for i in range(index+1,len(train_name_file)):
        copyfile(path_overwrite + train_name_file[i], '/storage/haibn/yt8m/2/data_suffer/' + train_name_file[i])

