import os
import subprocess
from json import loads
from re import escape
from string import lstrip

from flask import Flask, render_template, request, url_for, redirect, Response, send_file, jsonify
from werkzeug.utils import secure_filename

from dbutils.ChatTable import ChatTable
from dbutils.DataTable import DataTable
from dbutils.FileTable import FileTable
from dbutils.MessageTable import MessageTable
from dbutils.UserTable import UserTable

app = Flask(__name__)

ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_FILE_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'flac', 'm4a', 'mp4', 'apk'}

app.config['DATA_DIR'] = os.environ['IHS_DATA_DIR']
app.config['APP_DIR'] = os.environ['IHS_APP_DIR']


def allowed_photo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_PHOTO_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_FILE_EXTENSIONS


@app.route("/")
def home():
    if not DataTable().is_initialized():
        UserTable().create()
        ChatTable().create()
        FileTable().create()
        MessageTable().create()
        DataTable().set_initialization(1)
        return redirect(url_for('initialization'))
    else:
        pass
    ut = UserTable()
    if ut.get(attr='user_name') is None:
        return redirect(url_for('initialization'))
    else:
        return render_template('index.html', user_name=ut.get(attr='user_name'),
                               user_description=ut.get(attr='user_description'))


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
        return redirect(url_for('home'))
    else:
        return '''
        <!doctype html>
        <title>First time login</title>
        <h1>Enter you details</h1>
        <form action="" method=post enctype=multipart/form-data>
            Name : <input type=text name=user_name>
            About yourself : <input type=text name=user_description>
             <input type=submit value=Done>
        </form>
        '''


@app.route("/profilePicture_<size>")
def profile_picture(size):
    try:
        return send_file(app.config['DATA_DIR'] + "profilePicture_" + size + ".jpg", mimetype="image/jpeg")
    except IOError:
        return send_file(app.config['DATA_DIR'] + "blank.jpg", mimetype="image/jpeg")


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


@app.route("/editDescription", methods=['POST'])
def edit_description():
    description = request.form['description']
    ut = UserTable()
    description = escape(description)
    ut.edit(description)
    return redirect(url_for('home'))


@app.route("/get<category>Messages")
def get_personal_messages(category):
    mt = MessageTable()
    messages = mt.get(category=category)
    if messages is False:
        messages_json_response = '{ "messages" : [{"count": "0"}]}'
    else:
        messages_json_response = '{ "messages" : [{"count": "' + str(len(messages) + 1) + '"},'
        for message in messages:
            message_date = lstrip(str(message[4]), 'datetime.date')
            messages_json_response += '{"mid": "' + str(message[0]) + '", "m_data": "' + message[
                1] + '", "m_sender": "' + message[3] + '", "m_date": "' + str(message_date) + '"},'
        messages_json_response = messages_json_response[:-1]
        messages_json_response += ']}'
    return Response(messages_json_response, mimetype='application/json')


@app.route("/uploadFiles", methods=['POST'])
def upload_file():
    temp_file = request.files['file']
    if temp_file and allowed_file(temp_file.filename):
        filename = secure_filename(temp_file.filename)
        temp_file.save(os.path.join(app.config['DATA_DIR'], filename))
        ft = FileTable()
        ft.insert(filename, filename.rsplit('.', 1)[1])
        if filename.rsplit('.', 1)[1] in {"jpg", "png", "JPG", "PNG", "jpeg", "JPEG"}:
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
                                     shell=False) and not subprocess.check_call(
            ["rm", "-f", app.config['DATA_DIR'] + filename], shell=False):
            ft.remove(filename)
    except subprocess.CalledProcessError as e:
        print e
    return redirect(url_for('home'))


@app.route("/thumbnail_<file_name>")
def get_thumbnail(file_name):
    if file_name.rsplit('.', 1)[1] in ALLOWED_PHOTO_EXTENSIONS:
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


@app.route("/keyExchange")
def key_exchange():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", 42000))
    sock.listen(1)
    sock.settimeout(300)
    user_identity = ""
    try:
        conn, address = sock.accept()
    except socket.timeout:
        return jsonify({'user': user_identity})
    while 1:
        data = conn.recv(1024)
        if not data:
            break
        else:
            user_identity += data
    sock.close()
    return jsonify({'user': user_identity})


@app.route("/doKeyExchangeWith<email>", methods=["GET"])
def do_key_exchange(email):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", 42000))
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
            from xmlrpclib import ServerProxy
            s = ServerProxy("http://127.0.0.1:8080/")
            s.add_xmpp_user(email)
            success = True
    except socket.timeout as e:
        print e
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return jsonify({'success': success})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=True)
