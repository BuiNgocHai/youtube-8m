import pymysql
import sys
db = pymysql.connect("172.26.6.30",'haibn',password = '6uCp862BMhUJIQjpWCET')
sql = "select post_id,link,video_cate_1,video_cate_3 from kinghub.post_category \
where video_cate_1 is not null && video_cate_3 is null \
LIMIT 10"
insert_cmd = 'INSERT INTO kinghub.post_category(`post_id`,`card_type`,`link`, `link_crc32`, `video_cate_3`) \
                        VALUES( {},{},"{}",{},{} )'

# Execute the SQL command
args = insert_cmd.format(int(123433), 3, 'https://12278739077595283.lotuscdn.vn/121198567535677440/2020/1.mp4', int(23034912), int(30001))
print(args)
cursor = db.cursor()
cursor.execute( args)
db.commit()
# Fetch all the rows in a list of lists.
# results = cursor.fetchall()
# for item in results:
# print(item[1])

   #UPDate
#    cursor.execute('UPDATE kinghub.post_category set video_cate_3 = none ')
#    db.commit()
# except:
#     e = sys.exc_info()
#     print(e)
#     print ("Error: unable to fetch data")

# disconnect from server
db.close()