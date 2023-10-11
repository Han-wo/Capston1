from flask import Flask, render_template, Response
import socket
import cv2
import numpy as np
import struct

app = Flask(__name__)

# Server configuration
server_ip = '192.168.0.27'
port = 8485


def gen_frames():
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error in gen_frames(): {e}")
            client_socket.close()
            time.sleep(1)  # wait before reconnecting


@app.route('/')
def index():
    return render_template('streaming.html')


@app.route('/live_streaming', endpoint='live_streaming')
def live_streaming():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="192.168.0.30", port=8080, debug=True)
