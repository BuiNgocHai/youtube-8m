
from bs4 import BeautifulSoup as bs
import requests

base_url = 'https://www.youtube.com/results?search_query='
search_string = 'tin tức'
URL = base_url + search_string

response = requests.get(URL)
page = response.text


soup = bs(page, 'html.parser')
vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})

for v in vids:
    print(v['title'])
    v = str(v)
    views = ''
    try:
        indx = v.index('views')
        indx = indx - 2
        while v[indx] is not ' ':
            views = views + v[indx]
            indx = indx -1
        print(views[::-1])
    except:
        continue