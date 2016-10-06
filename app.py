import cv2
import os
from xmlrpclib import ServerProxy

from flask import Flask, Response, jsonify, request

app = Flask(__name__)


@app.route("/initialization", methods=['GET', 'POST'])
def initialization():
    if request.method == 'GET':
        if os.path.exists('init_config'):
            return jsonify({'init': True})
        else:
            return jsonify({'init': False})
    else:
        with open('init_config', 'r') as init_config:
            init_config.write("True")


# TODO Convert this to POST request
@app.route("/dKE<email>", methods=["GET"])
def do_key_exchange(email):
    success = False
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", 42000))
        sock.listen(1)
        sock.settimeout(300)
        user_identity = ""
    except socket.error as e:
        print e
        return success
    try:
        conn, address = sock.accept()
        while True:
            data_email = conn.recv(1024)
            if not data_email:
                break
            else:
                user_identity += data_email
                conn.shutdown(socket.SHUT_RD)
        user_identity = unicode(user_identity, "utf-8")
        if email == user_identity:
            with open(app.config['DATA_DIR'] + 'limited-user_key', "rb") as file_stream:
                data = file_stream.read(1024)
                while data:
                    conn.send(data)
                    data = file_stream.read(1024)
            s = ServerProxy("http://127.0.0.1:8080/")
            if s.add_xmpp_user(str(email)):
                success = True
    except socket.timeout as e:
        print e
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return jsonify({'success': success})


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.cv.CV_CAP_PROP_FPS, 10)
        self.video.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.video.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image, [cv2.cv.CV_IMWRITE_JPEG_QUALITY, 25])
        return jpeg.tobytes()


@app.route("/videocam")
def video_feed():
    def gen(camera):
        try:
            while True:
                frame = camera.get_frame()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except cv2.error as e:
            print e
            exit(1)

    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/powerControl<state>")
def iot(state):
    s = ServerProxy("http://127.0.0.1:8080/")
    if state == unicode("get"):
        state = s.get_power_status()
    elif state == unicode("off"):
        if s.turn_off():
            state = 0
    elif state == unicode("on"):
        if s.turn_on():
            state = 1
    return jsonify({'state': state})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=True)
