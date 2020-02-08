import csv
import os
import subprocess

#convert csv file

def convert_csv_file(path,file_vid, file_name):
    write_data = []
    labels = []
    for video_file, label in csv.reader(open(file_name)):
        write_data.append(path +file_vid +'/'+video_file+'.mp4')
        labels.append(label)

    with open(file_name[:-4]+'_final.csv', mode='w') as output_file:
        for index in range(len(write_data)):
            data_final = []
            data_final.append(write_data[index])
            data_final.append(labels[index])
            writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(data_final) 

if __name__ == '__main__':
    path = '/storage1/haibn/crawl_yt8m/video/'
    for file_name in os.listdir(path):
        path_csv = path + file_name + '/'+ file_name +'_final.csv'
        path_tfrecord = '/storage1/haibn/crawl_yt8m/tfrecord/'+file_name+'.tfrecord'
        if(file_name[:5] == 'train'):
            cmd = 'python3 /storage/haibn/yt8m/code/video_classification/feature_extractor/vggish/convert_wav.py --input_videos_csv=' + path_csv
            subprocess.call(cmd, shell=True)
            convert_csv_file(path, file_name, path+file_name+'/'+file_name+'.csv')

        command_extract = 'python3 /storage/haibn/yt8m/code/video_classification/feature_extractor/extract_tfrecords_main.py --input_videos_csv=' + path_csv + ' --output_tfrecords_file=' + path_tfrecord + ' --video_of_thread=50'
        subprocess.call(command_extract, shell=True)

        
        