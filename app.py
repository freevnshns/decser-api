import os
import subprocess
from json import loads
from re import escape
from string import lstrip
from xmlrpclib import ServerProxy

from flask import Flask, render_template, request, url_for, redirect, Response, send_file, jsonify
from werkzeug.utils import secure_filename

from dbutils.ChatTable import ChatTable
from dbutils.DataTable import DataTable
from dbutils.FileTable import FileTable
from dbutils.UserTable import UserTable

app = Flask(__name__)

app.config['DATA_DIR'] = os.environ['IHS_DATA_DIR']
app.config['APP_DIR'] = os.environ['IHS_APP_DIR']


def allowed_photo(filename):
    return '.' in filename and str(filename).lower().rsplit('.', 1)[1] in {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and str(filename).lower().rsplit('.', 1)[1] in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
                                                                           'mp3', 'flac', 'm4a', 'mp4', 'apk'}


@app.route("/")
def home():
    if not DataTable().is_initialized():
        UserTable().create()
        ChatTable().create()
        FileTable().create()
        DataTable().set_initialization(1)
        return redirect(url_for('initialization'))
    else:
        pass
    ut = UserTable()
    if ut.get(attr='user_name') in [None, '']:
        return redirect(url_for('initialization'))
    else:
        return render_template('index.html', user_name=ut.get(attr='user_name'),
                               user_description=ut.get(attr='user_description'))


# TODO setup xmpp account , backup account ,here...
@app.route("/initialization", methods=['GET', 'POST'])
def initialization():
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_description = request.form['user_description']
        ut = UserTable()
        if user_description is not u'':
            ut.insert(user_name, user_description)
        else:
            ut.insert(user_name)
        return redirect('/owncloud')
    else:
        return render_template('initialization.html')


@app.route("/changeProfilePicture", methods=['GET', 'POST'])
def change_profile_picture():
    if request.method == 'POST':
        temp_file = request.files['file']
        if temp_file and allowed_photo(temp_file.filename):
            temp_file.save(os.path.join(app.config['DATA_DIR'], "profilePicture.jpg"))
            try:
                subprocess.check_call(["/bin/bash", app.config['APP_DIR'] + "scripts/" + "reduce_image.sh"],
                                      shell=False)
            except subprocess.CalledProcessError as e:
                print e
            return redirect(url_for('home'))
    return '''
    <!doctype html>
    <title>Upload new Display Picture</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route("/profilePicture_<size>")
def profile_picture(size):
    try:
        return send_file(app.config['DATA_DIR'] + "profilePicture_" + size + ".jpg", mimetype="image/jpeg")
    except IOError:
        return send_file(app.config['DATA_DIR'] + "blank.jpg", mimetype="image/jpeg")


@app.route("/editDescription", methods=['POST'])
def edit_description():
    description = request.form['description']
    ut = UserTable()
    description = escape(description)
    ut.edit(description)
    return redirect(url_for('home'))


@app.route("/uploadFiles", methods=['POST'])
def upload_file():
    temp_file = request.files['file']
    if temp_file and allowed_file(temp_file.filename):
        filename = secure_filename(temp_file.filename)
        temp_file.save(os.path.join(app.config['DATA_DIR'], filename))
        ft = FileTable()
        ft.insert(filename, filename.rsplit('.', 1)[1])
        if allowed_photo(filename):
            try:
                subprocess.check_call(
                    ["/bin/bash", app.config['APP_DIR'] + "scripts/" + "create_thumbs.sh", filename],
                    shell=False)
            except subprocess.CalledProcessError as e:
                print e
    return redirect(url_for('home'))


@app.route("/getFileList")
def get_file_list():
    ft = FileTable()
    files = ft.get()
    if files is False:
        files_json_response = '{ "files" : [{"count": "0"}]}'
    else:
        files_json_response = '{ "files" : [{"count": "' + str(len(files) + 1) + '"},'
        for temp_file in files:
            message_date = lstrip(str(temp_file[1]), 'datetime.date')
            files_json_response += '{"file_name": "' + str(temp_file[0]) + '", "file_type": "' + temp_file[
                2] + '", "file_date": "' + str(message_date) + '"},'
        files_json_response = files_json_response[:-1]
        files_json_response += ']}'
    return Response(files_json_response, mimetype='application/json')


@app.route("/deleteFile_<filename>")
def delete_file(filename):
    ft = FileTable()
    try:
        if not subprocess.check_call(["rm", "-f", app.config['DATA_DIR'] + filename + "_thumbs.png"],
                                     shell=False) or not subprocess.check_call(
            ["rm", "-f", app.config['DATA_DIR'] + filename], shell=False):
            ft.remove(filename)
    except subprocess.CalledProcessError as e:
        print e
    return redirect(url_for('home'))


@app.route("/thumbnail_<file_name>")
def get_thumbnail(file_name):
    if allowed_photo(file_name):
        return send_file(app.config['DATA_DIR'] + file_name + "_thumbs.png", mimetype="image/png")
    else:
        return send_file(app.config['DATA_DIR'] + "icons/img_icons/document_icon.png", mimetype="image/png")


@app.route("/chatUpdates", methods=["POST"])
def chat_update():
    ct = ChatTable()
    chat_message = loads(request.data)
    ct.insert(escape(chat_message['chat_message']), escape(chat_message['chat_message_sender']))
    return Response('{"status":"ok"}', mimetype='application/json')


@app.route("/retrieveChat")
def retrieve_chat():
    ct = ChatTable()
    chat_messages = ct.get()
    chat_messages_json_response = '{ "chat_messages" : [{"count": "' + str(len(chat_messages) + 1) + '"},'
    for chat_message in chat_messages:
        message_date = lstrip(str(chat_message[1]), 'datetime.date')
        message_time = lstrip(str(chat_message[2]), 'datetime.time')

        chat_messages_json_response += '{"chat_message_sender": "' + str(chat_message[0]) + '", "chat_message": "' + \
                                       chat_message[
                                           3] + '", "chat_message_date": "' + str(
            message_date) + '","chat_message_time": "' + str(message_time) + '"},'
    chat_messages_json_response = chat_messages_json_response[:-1]
    chat_messages_json_response += ']}'
    return Response(chat_messages_json_response, mimetype='application/json')


# TODO Convert this to POST request
@app.route("/dKE<email>", methods=["GET"])
def do_key_exchange(email):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", 42000))
    except socket.error as e:
        print e
    sock.listen(1)
    sock.settimeout(300)
    user_identity = ""
    success = False
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


@app.route("/videocam")
def video_feed():
    import cv2

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
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()

    def gen(camera):
        try:
            while True:
                frame = camera.get_frame()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except cv2.error as e:
            print e

    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/powerControl<state>")
def iot(state):
    success = False
    s = ServerProxy("http://127.0.0.1:8080/")
    if state == unicode("off"):
        if s.turn_off():
            success = True
    elif state == unicode("on"):
        if s.turn_on():
            success = True
    return jsonify({'success': success})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=True)
