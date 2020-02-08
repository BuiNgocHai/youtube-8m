import os 

path = '/storage/haibn/yt8m/2/video_news/'
i = 0
for file_name in os.listdir(path):
    os.renames(path+file_name,path+'train'+str(i)+'new.mp4')
    i+=1
