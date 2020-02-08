import os
import cv2
import json
with open('labels_vietname/labels_train.json') as f:
    data_train = json.load(f)
with open('labels_vietname/labels_test.json') as f:
    data_test = json.load(f)


for file_name in os.listdir('../vietnam_ocr/Data_Noba_For_OCR/'):
    for name_img in os.listdir('../vietnam_ocr/Data_Noba_For_OCR/'+file_name):
        if (name_img[:5] != 'label'):
                img = cv2.imread('../vietnam_ocr/Data_Noba_For_OCR/'+file_name +'/'+name_img)
                print('writing ', name_img)
                cv2.imwrite('../data_vn/' + name_img,img)

for key in data_test:
    img = cv2.imread('..'+data_test[key][0]['path'])
    cv2.imwrite('../data_vietnam/val/'+data_test[key][0]['path'][:9],img)

for key in data_train:
    img = cv2.imread('..'+data_train[key][0]['path'])
    cv2.imwrite('../data_vietnam/train/'+data_train[key][0]['path'][:9],img)