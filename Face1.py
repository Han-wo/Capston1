import cv2
import numpy as np
import firebase_admin
from firebase_admin import storage, credentials
import os

# Firebase Cloud Storage 초기화
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(
    cred, {'storageBucket': 'capston1-771fd.appspot.com'})
bucket = storage.bucket()

# 얼굴 인식용 xml 파일
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


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


cap = cv2.VideoCapture(0)
count = 0


if not os.path.exists('faces'):
    os.makedirs('faces')

while True:
    ret, frame = cap.read()
    if face_extractor(frame) is not None:
        count += 1
        face = cv2.resize(face_extractor(frame), (200, 200))
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

        # Firebase Storage에 저장할 파일 이름
        file_name_path = 'faces/user'+str(count)+'.jpg'

        # 로컬에 임시 파일로 저장
        # cv2.imwrite(file_name_path, face)
        _, img_encoded = cv2.imencode('.jpg', face)
        with open(file_name_path, 'wb') as file_obj:
            file_obj.write(img_encoded.tostring())

            # 파일이 완전히 쓰여졌는지 확인
            os.fsync(file_obj.fileno())

        # Firebase Cloud Storage에 업로드
        blob = bucket.blob(file_name_path)
        blob.upload_from_filename(file_name_path)

        # 업로드가 완료되었는지 확인
        assert blob.exists()

        # 로컬에 저장된 임시 파일 삭제
        os.remove(file_name_path)

        cv2.putText(face, str(count), (50, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Face Cropper', face)
    else:
        print("Face not Found")
        pass

    if cv2.waitKey(1) == 13 or count == 100:
        break

cap.release()
cv2.destroyAllWindows()
print('Collecting Samples Complete!!!')
