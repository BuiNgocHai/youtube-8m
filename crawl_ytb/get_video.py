import wget
import pandas as pd
from pandas import DataFrame

def get_video(link,name):

    print('get video from :' + str(link))
    url = link
    wget.download(url, '/storage/haibn/yt8m/test_lotus/' + name)

data = pd.read_csv('output_file.csv')
value = data.values
count = 0
name_of_video = []
links = []
for val in value:
    index = val[0].find('\t')
    link = val[0][index+1:len(val[0])]
    try:
        name = 'lotus_video_' + str(count) + '.mp4'
        get_video(link,name)
        name_of_video.append(name)
        links.append(link)
        count+=1
    except:
        print('False in ' + link)
        continue
lotus_video = {'name' : name_of_video,'link' : links}
df = DataFrame(lotus_video, columns= ['name', 'link'])
df.to_csv('output_file_1.csv',index=False)

print('Cawrl ' + str(count))
