select count(*) from kinghub.post_category
where video_cate_3 is not null && video_cate_1 is null
LIMIT 10

select post_id,link,video_cate_1,video_cate_3 from kinghub.post_category
where post_id = 666587327919005696

659697416691490816              

UPDATE kinghub.post_category
SET video_cate_3 = 30000
WHERE post_id = 659676678460243968	&& link_crc32 = 32250769

INSERT INTO kinghub.post_category(`post_id`,`card_type`,`link`, `link_crc32`, `video_cate_3`) 
VALUES(660450540288184320, 3, 'abc.mp4', 123, 3000)

665159392275435520
664436109658529792

select * from adnetwork_task.youtube_crawler