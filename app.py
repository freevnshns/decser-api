import os
import subprocess
from re import escape
from string import lstrip
from json import loads

from flask import Flask, render_template, request, url_for, redirect, Response, send_file
from werkzeug.utils import secure_filename

from dbutils.user_table import usertable
from dbutils.messages_table import messages_table
from dbutils.files_table import files_table
from dbutils.chat_table import chat_table


app = Flask(__name__, static_folder='/var/www/comslav/secureAdminDash/front/static',
            template_folder='/var/www/comslav/secureAdminDash/front/public_html')
SHELL_SCRIPTS_FOLDER = '/var/www/comslav/secureAdminDash/cron_jobs/'
USER_ASSETS_FOLDER = '/home/comslav/user_assets/'
UPLOADED_FILES_FOLDER = '/home/comslav/user_file_uploads/'
ASSETS_FOLDER = '/var/www/comslav/secureAdminDash/front/static/'
ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'}
ALLOWED_FILE_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp3','flac','m4a','mp4'}

app.config['USER_ASSETS_FOLDER'] = USER_ASSETS_FOLDER
app.config['UPLOADED_FILES_FOLDER'] = UPLOADED_FILES_FOLDER

def allowed_photo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_PHOTO_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_FILE_EXTENSIONS


@app.route("/")
def home():
    ut = usertable()
    if ut.get(attr='user_info') is False:
        return redirect(url_for('initialization'))
    else:
        index_response = Response(
            render_template('index.html', user_name=ut.get(attr='user_name'), user_info=ut.get(attr='user_info')))
        return index_response

@app.route("/initialization", methods=['GET','POST'])
def initialization():
    if request.method == 'POST':
        uname = request.form['uname']
        udesc = request.form['udesc']
        ut = usertable()
        if udesc is not u'':
            ut.insert(uname,udesc)
        else:
            ut.insert(uname)
        file = request.files['file']
        if file and allowed_photo(file.filename):
            file.save(os.path.join(app.config['USER_ASSETS_FOLDER'], "profilePicture.jpg"))
            try:
                subprocess.check_call(["/bin/bash", SHELL_SCRIPTS_FOLDER + "reduce_image.sh"],
                                      shell=False)
            except subprocess.CalledProcessError as e:
                print e
            return redirect(url_for('home'))
    return '''
    <!doctype html>
    <title>First time login</title>
    <h1>Upload a Picture of yours</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
        Name : <input type=text name=uname>
        About yourself : <input type=text name=udesc>
         <input type=submit value=Done>
    </form>
    '''



@app.route("/profilePicture_<size>")
def profilePicture(size):
    return send_file(USER_ASSETS_FOLDER + "profilePicture_"+size+".jpg", mimetype="image/jpeg")




@app.route("/changeProfilePicture", methods=['GET', 'POST'])
def uploadProfilePicture():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_photo(file.filename):
            file.save(os.path.join(app.config['USER_ASSETS_FOLDER'], "profilePicture.jpg"))
            try:
                subprocess.check_call(["/bin/bash", SHELL_SCRIPTS_FOLDER + "reduce_image.sh"],
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
def editDescription():
    description = request.form['description']
    ut = usertable()
    description = escape(description)
    ut.edit(description)
    return redirect(url_for('home'))


@app.route("/get<category>Messages")
def getPersonalMessages(category):
    mt = messages_table()
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
def uploadFiles():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOADED_FILES_FOLDER'], filename))
        ft = files_table()
        ft.insert(filename, filename.rsplit('.', 1)[1])
        if (filename.rsplit('.', 1)[1] in {"jpg", "png", "JPG", "PNG", "jpeg", "JPEG"}):
            try:
                subprocess.check_call(
                    ["/bin/bash", SHELL_SCRIPTS_FOLDER + "create_thumbs.sh", filename],
                    shell=False)
            except subprocess.CalledProcessError as e:
                print e
    return redirect(url_for('home'))


@app.route("/getFileList")
def getFileList():
    ft = files_table()
    files = ft.get()
    if files is False:
        files_json_response = '{ "files" : [{"count": "0"}]}'
    else:
        files_json_response = '{ "files" : [{"count": "' + str(len(files) + 1) + '"},'
        for file in files:
            message_date = lstrip(str(file[1]), 'datetime.date')
            files_json_response += '{"file_name": "' + str(file[0]) + '", "file_type": "' + file[
                2] + '", "file_date": "' + str(message_date) + '"},'
        files_json_response = files_json_response[:-1]
        files_json_response += ']}'
    return Response(files_json_response, mimetype='application/json')


@app.route("/deleteFile_<filename>")
def deleteFile(filename):
    ft = files_table()
    try:
        if not subprocess.check_call(["rm", "-f", UPLOADED_FILES_FOLDER + filename + "_thumbs.png"],
                                     shell=False) and not subprocess.check_call(
                ["rm", "-f", UPLOADED_FILES_FOLDER + filename], shell=False):
            ft.remove(filename)
    except subprocess.CalledProcessError as e:
        print e
    return redirect(url_for('home'))


@app.route("/thumbnail_<file_name>")
def getThumbnail(file_name):
    if file_name.rsplit('.', 1)[1] in ALLOWED_PHOTO_EXTENSIONS:
        return send_file(UPLOADED_FILES_FOLDER + file_name + "_thumbs.png", mimetype="image/png")
    else:
        return send_file(ASSETS_FOLDER+"icons/img_icons/document_icon.png", mimetype="image/png")


@app.route("/chatUpdates", methods=["POST"])
def chatUpdates():
    ct = chat_table()
    chat_message = loads(request.data)
    ct.insert(escape(chat_message['chat_message']), escape(chat_message['chat_message_sender']))
    return Response('{"status":"ok"}', mimetype='application/json')


@app.route("/retrieveChat")
def retrieveChat():
    ct = chat_table()
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

#To Be Implemented next
# @app.route("/addNote")
# def addNote():


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)

