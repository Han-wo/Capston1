import cv2
import tensorflow as tf
import datetime
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, Response, request, session, redirect
from functools import wraps
import re
import hashlib
import socket
import numpy as np
import struct
import time


app = Flask(__name__)
app.secret_key = 'capston1_4'

# Server configuration
server_ip = '192.168.0.27'
port = 8485

# 전역 소켓 연결
client_socket = None

# Firebase Admin SDK 초기화
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://capston1-771fd-default-rtdb.firebaseio.com/'
})

ref_logs = db.reference('logs')

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# 모델 로드
model = tf.keras.models.load_model('model/keras_model.h5')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def gen_frames():
    global client_socket
    while True:
        try:
            if client_socket is None:
                client_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_ip, port))

            while True:
                data_size = struct.unpack("I", client_socket.recv(4))[0]
                frame_data = b''
                while len(frame_data) < data_size:
                    recv_data = client_socket.recv(
                        min(1024, data_size - len(frame_data)))
                    if not recv_data:
                        break
                    frame_data += recv_data

                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                frame = cv2.flip(frame, 1)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray,
                                                      scaleFactor=1.1,
                                                      minNeighbors=5,
                                                      minSize=(30, 30),
                                                      flags=cv2.CASCADE_SCALE_IMAGE)

                now = datetime.datetime.now()
                date = now.strftime('%Y-%m-%d')
                current_time = now.strftime('%H:%M:%S')

                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        face_img = gray[y:y+h, x:x+w]
                        resized_img = cv2.resize(face_img, (224, 224))
                        rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_GRAY2RGB)
                        normalized_img = rgb_img / 255.0
                        reshaped_img = np.reshape(normalized_img, (1, 224, 224, 3))
                        result = model.predict(reshaped_img)

                        if result[0][0] > 0.7:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, 'Pass', (x, y-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            ref_logs.push({
                                'date': date,
                                'time': current_time,
                                'is_registered': 'Registered'
                            })
                        else:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                            cv2.putText(frame, 'X', (x, y-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                            ref_logs.push({
                                'date': date,
                                'time': current_time,
                                'is_registered': 'Unregistered'
                            })

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except Exception as e:
            print(f"Error in gen_frames(): {e}")
            client_socket.close()
            client_socket = None
            time.sleep(1)


@app.route('/')
def index():
    if 'user' in session:
        logs = ref_logs.get()

        log_list = []
        if logs:
            for key, log in logs.items():
                log['key'] = key
                log['datetime'] = datetime.datetime.strptime(
                    log['date'] + ' ' + log['time'], '%Y-%m-%d %H:%M:%S')
                log_list.append(log)

        log_list = sorted(log_list, key=lambda x: x['datetime'], reverse=True)
        return render_template('streaming.html', logs=log_list[:10])
    else:
        return redirect('/login')


@app.route('/logs')
@login_required
def logs():
    logs = ref_logs.get()

    log_list = []
    if logs:
        for key, log in logs.items():
            log['key'] = key
            log['datetime'] = datetime.datetime.strptime(
                log['date'] + ' ' + log['time'], '%Y-%m-%d %H:%M:%S')
            log_list.append(log)

    log_list = sorted(log_list, key=lambda x: x['datetime'], reverse=True)

    return render_template('logs.html', logs=log_list)


@app.route('/live_streaming')
@login_required
def live_streaming():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        password = hashlib.sha256(password.encode()).hexdigest()
        try:
            # Realtime Database에서 유저 정보 가져오기
            users_ref = db.reference('users')
            query = users_ref.order_by_child('email').equal_to(email)
            results = query.get()
            user_id = list(results.keys())[0]
            user = results[user_id]
            if user['password'] == password:

                # 세션에 유저 정보 저장하기
                session['user'] = {'uid': user_id, 'email': email}
                # 로그인 성공시 / 주소로 redirect
                return redirect('/')

            else:
                return render_template('login.html', message='이메일이나 비밀번호가 일치하지 않습니다.')
        except Exception as e:
            return render_template('login.html', message='이메일이나 비밀번호가 일치하지 않습니다.')
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # 이메일 유효성 검사
        if not re.match(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return render_template('signup.html', message='이메일 형식이 올바르지 않습니다.')

        # 비밀번호 유효성 검사
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+\\\|\[\]{};\':"\\,.<>\/?])([A-Za-z\d!@#$%^&*()\-_=+\\\|\[\]{};\':"\\,.<>\/?]{8,})$', password):
            return render_template('signup.html', message='비밀번호는 영문, 숫자, 특수문자를 조합한 8자리 이상이어야 합니다.')

        # 비밀번호를 해시로 변환
        password = hashlib.sha256(password.encode()).hexdigest()

        try:
            # Realtime Database에서 이미 등록된 이메일인지 확인하기
            ref = db.reference('users')
            snapshot = ref.order_by_child('email').equal_to(email).get()
            if snapshot:
                return render_template('signup.html', message='이미 등록된 이메일입니다.')

            # Realtime Database에 유저 정보 저장하기
            ref.push({
                'email': email,
                'phone': phone,
                'password': password
            })

            return "<script>alert('회원가입이 완료되었습니다.');location.href='/login';</script>"
        except Exception as e:
            return render_template('signup.html', message=f'회원가입 중 오류가 발생했습니다.{(e)}')
    else:
        return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(host="192.168.0.30", port=8080, debug=True)
