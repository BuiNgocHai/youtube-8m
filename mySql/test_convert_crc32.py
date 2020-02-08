import zlib
mystring = 'https://hls.mediacdn.vn/kingcontent/2019/3/5/bt-sieu-nang-luc-moi-co-nguoi-thai-ra-duoc-cuc-phan-sieu-cuong-tri-duoc-nhieu-benh-nghiem-trong-cn-1551756597784277791279-05685.mp4'
s = bytes(mystring, 'utf-8')
prev = zlib.crc32(s,0)
print(prev)