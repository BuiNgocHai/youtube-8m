from bs4 import BeautifulSoup as bs
import requests
from pytube import YouTube
base = "https://www.youtube.com/results?search_query="
qstring = "tin tức"

r = requests.get(base+qstring)

page = r.text
soup=bs(page,'html.parser')
vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})
videolist=[]
for v in vids:
    tmp = 'https://www.youtube.com' + v['href']
    videolist.append(tmp)

print(videolist)

count=0
for item in videolist:
 
    # increment counter:
    count+=1
 
    # initiate the class:
    yt = YouTube(item)
 
    # have a look at the different formats available:
    #formats = yt.get_videos()
 
    # grab the video:
    video = yt.get_videos('mp4', '360p')
 
    # set the output file name:
    yt.set_filename('Video_'+str(count))
 
    # download the video:
    video.download('./')