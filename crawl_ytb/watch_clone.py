import os
import subprocess
import sys


while(1):
    if len(os.listdir('2/done/')) == 0:
        print('Folder empty')
    else:
        for file_name in os.listdir('2/done/'):
            print(file_name[:-4])
            name = file_name[:-4]

            #remove webm
            command = 'rm -rf ' + '2/video/' + name + '/*.webm'

            try:
                subprocess.call(command, shell=True)
            except:
                e = sys.exc_info()
                print(e)
                raise IOError('Can not remove webm')
            #zip file
            command = 'zip -r ' + '2/driver/' + name +'.zip 2/video/' + name + '/'
            try:
                subprocess.call(command, shell=True)
            except:
                e = sys.exc_info()
                print(e)
                raise IOError('Can not zip file')

            #reomve video 
            command = 'rm -rf 2/video/' + name + '/*.mp4'
            try:
                subprocess.call(command, shell=True)
            except:
                e = sys.exc_info()
                print(e)
                raise IOError('Can not delete video file')

            #upload zip
            command = 'rclone copy -vv 2/driver/' + name +'.zip remote:/crawl_yt8m'
            try:
                subprocess.call(command, shell=True)
            except:
                e = sys.exc_info()
                print(e)
                raise IOError('Can not upload file')

            #delete zip 
            command = 'rm -rf 2/driver/' + name + '.zip'
            try:
                subprocess.call(command, shell=True)
            except:
                e = sys.exc_info()
                print(e)
                raise IOError('Can not  delete zip file')

            #remove csv file
            command = 'rm -rf 2/done/' + file_name
            try:
                subprocess.call(command, shell=True)
            except:
                e = sys.exc_info()
                print(e)
                raise IOError('Can not delete csv file')

            f=open("done.txt", "a+")
            f.write(file_name)


