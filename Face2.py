# import cv2
# import numpy as np
# from os import listdir
# from os.path import isfile, join

# data_path = 'faces/'
# onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path,f))]

# Training_Data, Labels = [], []

# for i, files in enumerate(onlyfiles):
#     image_path = data_path + onlyfiles[i]
#     images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     Training_Data.append(np.asarray(images, dtype=np.uint8))
#     Labels.append(i)

# Labels = np.asarray(Labels, dtype=np.int32)

# model = cv2.face.LBPHFaceRecognizer_create()

# model.train(np.asarray(Training_Data), np.asarray(Labels))

# print("Model Training Complete!!!!!")

import cv2
import numpy as np
import firebase_admin
from firebase_admin import storage, credentials
import os
import numpy as np
from os import listdir
from os.path import isfile, join

# Firebase Cloud Storage 초기화
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(
    cred, {'storageBucket': 'capston1-771fd.appspot.com'})
bucket = storage.bucket()

# 얼굴 인식용 xml 파일
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Training_Data와 Labels 변수 정의
Training_Data, Labels = [], []


def face_extractor(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return None

    # 가장 큰 얼굴 영역 선택
    max_area = 0
    max_idx = 0
    for i, (x, y, w, h) in enumerate(faces):
        area = w * h
        if area > max_area:
            max_area = area
            max_idx = i

    (x, y, w, h) = faces[max_idx]
    cropped_face = img[y:y+h, x:x+w]

    return cropped_face


# Firebase Storage에서 이미지 다운로드하여 학습 데이터로 사용
data_path = 'faces/'
onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]

Training_Data, Labels = [], []

for i, files in enumerate(onlyfiles):
    image_path = data_path + onlyfiles[i]
    images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if images is not None:
        Training_Data.append(np.asarray(images, dtype=np.uint8))
        label = int(''.join(filter(str.isdigit, onlyfiles[i])))
        Labels.append(label)

if len(Labels) == 0:
    print("학습된 데이터셋이 없습니다.")
    exit()

Labels = np.asarray(Labels, dtype=np.int32)

model = cv2.face.LBPHFaceRecognizer_create()
model.train(np.asarray(Training_Data), np.asarray(Labels))

print("모델 학습이 완료 되었습니다")
