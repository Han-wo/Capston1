from firebase_admin import db
from app import app
from flask import Response
from flask import Flask, render_template, Response, request, session, redirect
import cv2
import random
import datetime
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = 'capston1_4'

# Firebase Admin SDK 초기화
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://capston1-771fd-default-rtdb.firebaseio.com/'
})

ref_logs = db.reference('logs')

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


def gen_frames():
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = capture.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray,
                                                  scaleFactor=1.1,
                                                  minNeighbors=5,
                                                  minSize=(30, 30),
                                                  flags=cv2.CASCADE_SCALE_IMAGE)
            # 얼굴이 인식되면
            if len(faces) > 0:
                now = datetime.datetime.now()
                date = now.strftime('%Y-%m-%d')
                time = now.strftime('%H:%M:%S')

                # 랜덤으로 얼굴이 등록되었는지 여부 기록
                is_registered = random.choice([True, False])

                # 출입로그 데이터 작성
                log = {
                    'date': date,
                    'time': time,
                    'is_registered': is_registered
                }

                # Firebase에 출입로그 데이터 추가
                ref_logs.push(log)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    capture.release()


@app.route('/')
def index():
    if 'user' in session:
        return render_template('streaming.html')
    else:
        return redirect('/login')


@app.route('/live_streaming')
def live_streaming():
    if 'user' in session:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return redirect('/login')


@app.route('/logs')
def logs():
    logs = ref_logs.get()

    log_list = []
    if logs:
        for key, log in logs.items():
            log['key'] = key
            log_list.append(log)

    log_list = sorted(log_list, key=lambda x: x['time'], reverse=True)

    return render_template('logs.html', logs=log_list)


if __name__ == "__main__":
    app.run(debug=True)
