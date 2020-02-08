from pytube import Playlist, YouTube

def getAllLinks(playList):

    allLinks = []
    youtubeLink = 'https://www.youtube.com'
    pl = Playlist(playList)
    for linkprefix in pl.parse_links():
        allLinks.append(youtubeLink + linkprefix)
    return allLinks


select = input('Select you playlist: ')

l = ['https://www.youtube.com/watch?v=Edpy1szoG80&list=PL153hDY-y1E00uQtCVCVC8xJ25TYX8yPU',
    'https://www.youtube.com/playlist?list=PLrMWHlXIYbHUouLPA9Tp1LkcxUZqMwRVW',
    'https://www.youtube.com/watch?v=Q8K3Pxwfm5w&list=PLWAEeuXr_ATTXnorh9OmqLmCImLQwgxwL',
    'https://www.youtube.com/playlist?list=PLxv6taYbRuB76UQSq2HllKxLDQY5vGjhv',
    'https://www.youtube.com/playlist?list=PLrMWHlXIYbHUj677ueY8UPcbKCCoiUrpL',
    'https://www.youtube.com/playlist?list=PLBseYXEHNNPgX5X55X5kLDQ6kG1_E19V8',
    'https://www.youtube.com/playlist?list=PL72acOCPGU7olvso4HTw9vrej-o6eazc4',
    'https://www.youtube.com/playlist?list=PL231429C17BE39E34',
    'https://www.youtube.com/playlist?list=PLWAEeuXr_ATTXnorh9OmqLmCImLQwgxwL',
    'https://www.youtube.com/playlist?list=PLlGhOZ-L6WxDKyt6T82RePfqNYFXd4Amt',
    'https://www.youtube.com/playlist?list=PL3tD9HNke1uQTiTYZ8mhouKKFDScRYWXC',
    'https://www.youtube.com/playlist?list=PLLsO3pH5RkASAc0skj2SJVEiFfAnwHgOg',
    'https://www.youtube.com/playlist?list=PLjw6ZkpayzoDtfp4GJIp25NJwQ9HYmCGZ',
    'https://www.youtube.com/playlist?list=PLF3UjIBiVGVD0wysdQ1z-Qf9rs40Rc7vT',
    'https://www.youtube.com/playlist?list=PLF3UjIBiVGVDLgBpRrAlgfMCqgsp9KJgV',
    'https://www.youtube.com/playlist?list=PLF3UjIBiVGVByLavPvBm0zLfVFm4WjFci',
    'https://www.youtube.com/playlist?list=PLE9NY09xlfXNo9qdXb-iPOiLqH2rZppiE',
    'https://www.youtube.com/playlist?list=PLxv6taYbRuB4FvKELONLARCrq_qHxHUSK',
    'https://www.youtube.com/playlist?list=PLlxiEu-xZtZQ8K8ly8GiboU_isQPJKSlf',
    'https://www.youtube.com/playlist?list=PLyiHcrNa8dxj95kjysA__lMrVgPXGlveq',
    'https://www.youtube.com/playlist?list=PLyiHcrNa8dxgity0My7CCb_7iy_CDXHAJ',
    'https://www.youtube.com/playlist?list=PL1Vi4Nt_Cpb6PczKhpqZ07tmCIMurPXKg',
    'https://www.youtube.com/playlist?list=PL1Vi4Nt_Cpb5Ng9wVr1Dm6kAFtWcrmqmw',
    'https://www.youtube.com/playlist?list=PL1Vi4Nt_Cpb70vi2JBhNjPi02iWjTKX85',
    'https://www.youtube.com/playlist?list=PL1Vi4Nt_Cpb4icf3Q4xW3Y_WkqeL5ndHq',
    'https://www.youtube.com/playlist?list=PLmCtNp96hRy4zotGI5k9EqDZNX8ROvF9t',
    'https://www.youtube.com/playlist?list=PLvYpzlS_fYfhT9P_q5NrJ_UGq7vlFvkQl',
    'https://www.youtube.com/playlist?list=PL0Xd6_vQV82J52tOAeVFCnfGNy9mbQqH4',
    'https://www.youtube.com/playlist?list=PLLsO3pH5RkASlcKVfuVmrxueQa6zGGek8',
    'https://www.youtube.com/playlist?list=PLUuMQ0qR6n4wSR-Xe9eCk5WQpm9mdDKwy',
    'https://www.youtube.com/playlist?list=PLF3UjIBiVGVDk6lbHf1LBqx592uHKS6Ke',
    'https://www.youtube.com/playlist?list=PLbkz2ORJaK6jZBS6HbHqDwAGWgOn7VrAA'
    
    ]

linkArray = getAllLinks(l[int(select)])
total = len(linkArray)
num_of_vid = 0
print('The playlist have :'+total+' video')
for link in linkArray:
    try:
        print('dowload in list *', str(select)+'* : '+ link)
        YouTube(link).streams.first().download('/storage/haibn/yt8m/2/video_news/')
        num_of_vid +=1
    except:
        print('False in ' + link)
        continue
print('Downloaded '+num_of_vid +' /'+total) 

