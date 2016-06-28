function loadMessages(category) {
    "use strict";
    var xmlhttp;
    var message_obj;

    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    }
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 1) {
            if (category == "personal") {
                document.getElementById("messages-list-personal").innerHTML = "Loading .....";
            } else {
                document.getElementById("messages-list-work").innerHTML = "Loading .....";
            }
        }
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            message_obj = JSON.parse(xmlhttp.responseText);
            var message_list = "";
            var message_count = message_obj.messages[0].count;
            for (var i = 1; i < message_count; i++) {
                message_list += '<li class="accordion-navigation"><a href="#panel' + i + '">' + message_obj.messages[i].m_sender + '</a><div id="panel' + i + '" class="content">' + message_obj.messages[i].m_data + '</div></li>';
            }
            if (category == "personal") {
                document.getElementById("messages-list-personal").innerHTML = message_list;
            } else {
                document.getElementById("messages-list-work").innerHTML = message_list;
            }
        }
    };
    xmlhttp.open("GET", '/get' + category + 'Messages', true);
    xmlhttp.send();
}

function loadFiles() {
    "use strict";
    var xmlhttp;
    var file_obj;
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    }
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 1) {
            document.getElementById("file-list").innerHTML = "Loading .....";
        }
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            file_obj = JSON.parse(xmlhttp.responseText);
            var files_list = "";
            var file_count = file_obj.files[0].count;
            for (var i = 1; i < file_count; i++) {
                files_list += "<li>" + file_obj.files[i].file_name + "</li>";
            }
            document.getElementById("file-list").innerHTML = files_list;

        }
    };
    xmlhttp.open("GET", "/getFileList", true);
    xmlhttp.send();
}
function loadFilesDelete() {
    "use strict";
    var xmlhttp;
    var file_obj;
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    }
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 1) {
            document.getElementById("file-list-delete").innerHTML = "Loading .....";
        }
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            file_obj = JSON.parse(xmlhttp.responseText);
            var files_list = "";
            var file_count = file_obj.files[0].count;
            for (var i = 1; i < file_count; i++) {
                files_list += "<li><a href='deleteFile_"+file_obj.files[i].file_name+"'><img src='/thumbnail_" + file_obj.files[i].file_name + "' width='75'><br>"+file_obj.files[i].file_name+"</li>";
            }
            document.getElementById("file-list-delete").innerHTML = files_list;

        }
    };
    xmlhttp.open("GET", "/getFileList", true);
    xmlhttp.send();
}
function retrieveChat() {
    "use strict";
    var xmlhttp;
    var prev_responseText="";
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    }
    xmlhttp.onreadystatechange = function() {

        if (xmlhttp.readyState == 4 && xmlhttp.status == 200 && prev_responseText != xmlhttp.responseText) {
            prev_responseText = xmlhttp.responseText;
            var chat_message_JSON = JSON.parse(xmlhttp.responseText);
            var chat_message_count = chat_message_JSON.chat_messages[0].count;
            var chat_message_box = "";
            for (var i = 1; i < chat_message_count; i++) {
                if (chat_message_JSON.chat_messages[i].chat_message_date == chat_message_JSON.chat_messages[i-1].chat_message_date) {
                    chat_message_box += "<li>" + chat_message_JSON.chat_messages[i].chat_message_time + " : <b>" + chat_message_JSON.chat_messages[i].chat_message_sender + "</b> : <i>" + chat_message_JSON.chat_messages[i].chat_message + "</i></li>";
                } else {
                    chat_message_box += "<li>" + chat_message_JSON.chat_messages[i].chat_message_date+" "+chat_message_JSON.chat_messages[i].chat_message_time + " : <b>" + chat_message_JSON.chat_messages[i].chat_message_sender + "</b> : <i>" + chat_message_JSON.chat_messages[i].chat_message + "</i></li>";
                }
            }
            document.getElementById("chat_message_box").innerHTML = chat_message_box;
        }
    };
    xmlhttp.open("GET", "/retrieveChat", true);
    xmlhttp.send();
}
function send_chat_message(e) {
    "use strict";
    if (e.keyCode == 13) {
        var xmlhttp;
        if (window.XMLHttpRequest) {
            xmlhttp = new XMLHttpRequest();
        }
        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                var send_success = JSON.parse(xmlhttp.responseText);
                if (send_success.status == "ok") {
                    // document.getElementById("chat_message_box").innerHTML += "<li>" + chat_message_sender + " : " + chat_message + "</li>";
                    document.getElementById("chat_message").value = "";
                }
            }
        };
        var chat_message = document.getElementById("chat_message").value;
        var chat_message_sender = document.getElementById("chat_message_sender").value;
        var chat_message_JSON = JSON.stringify({
            "chat_message_sender": chat_message_sender,
            "chat_message": chat_message
        });
        xmlhttp.open("POST", "/chatUpdates", true);
        xmlhttp.setRequestHeader("Content-type", "application/json");
        xmlhttp.send(chat_message_JSON);
    }
    retrieveChat();
}
