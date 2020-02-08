from pytube import Playlist
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
    'https://www.youtube.com/playlist?list=PLE9NY09xlfXNo9qdXb-iPOiLqH2rZppiE']

#import pdb; pdb.set_trace()
pl = Playlist(l[int(select)])
#pl.download_all()

print('strart dowload ' + select)
pl.download_all('/home/vicker/Desktop/crawl_ytb/a')