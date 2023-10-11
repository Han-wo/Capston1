import cv2
import datetime
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, render_template
from threading import Thread
# from flask_paginate import Pagination

# Firebase 인증 정보
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://capston1-771fd-default-rtdb.firebaseio.com/'
})

# Firebase 참조
ref_logs = db.reference('logs')

# 얼굴 인식 모델 로드
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# 웹캠으로부터 프레임을 읽어올 객체 생성 라즈베리 파이 카메라로 수정해야함
cap = cv2.VideoCapture(0)

app = Flask(__name__)


@app.route('/')
def logs():
    # Firebase에서 출입 로그 가져오기
    logs = ref_logs.get()

    # 출입 로그 데이터 정제
    log_list = []
    if logs:
        for key, log in logs.items():
            log['key'] = key  # 로그의 키 추가
            log_list.append(log)

    # 최신 출입 로그부터 정렬
    log_list = sorted(log_list, key=lambda x: x['time'], reverse=True)

    return render_template('logs.html', logs=log_list)


def run():
    # # process_frame() 함수를 스레드로 실행
    # Thread(target=process_frame).start()

    # Flask 애플리케이션 실행
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    run()
