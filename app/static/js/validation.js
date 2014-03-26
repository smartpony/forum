// --- ФОРМЫ ПОСТИНГА ---------------------------
// Обработка сабмита формы. Если найдены пустые поля - выделить их красным и вернуть false.
function PostingFormValidate() {
    var res = true;
    // Введён ли текст сообщения
    var message = document.getElementById("message");
    if(message.value == "") {
        message.style.border = "1px solid #f06565";
        message.style.boxShadow = "0 0 1px 1px #f5b3b3";
        res = false;
    }
    // Введена ли тема + проверка наличия темы (для страницы топика)
    var topic = document.getElementById("topic");
    if(topic != null && topic.value == "") {
        topic.style.border = "1px solid #f06565";
        topic.style.boxShadow = "0 0 1px 1px #f5b3b3";
        res = false;
    }
    // Введён ли адресат сообщения + проверка наличия поля адреса (для личных сообщений)
    var recepient = document.getElementById("recepient");
    if(recepient != null && recepient.value == "") {
        recepient.style.border = "1px solid #f06565";
        recepient.style.boxShadow = "0 0 1px 1px #f5b3b3";
        res = false;
    }
    return res;
}

// При вводе данных снимать красное выделение.
function PostingFormUnmark(object) {
  if(object.value != "") {
    object.style.border = "1px solid #abadb3";
    object.style.boxShadow = "";
  }
}


// --- РЕДАКТИРОВАНИЕ ПРОФИЛЯ -------------------
// Выбран ли аватар
function ProfileFormValidate() {
    if(document.getElementById("new_avatar").innerHTML == "Only JPG, GIF or PNG")
        return false;
    else
        return true;
}

// Вывод имени выбранного файла аватара
function ShowAvatarName() {
    var new_avatar = document.getElementById("avatar").value;
    var allowed_ext = ["jpg", "jpeg", "gif", "png"];
    // Исключить полный путь и оставить только имя
    new_avatar = new_avatar.replace(/^.*[\\\/]/, "");

    if(new_avatar.value != "") {
        var avatar_ext = new_avatar.split(".").pop().toLowerCase();
        if(allowed_ext.indexOf(avatar_ext) != -1) {
            document.getElementById("new-avatar").style.color = "#505050";
            document.getElementById("new-avatar").innerHTML = new_avatar;
        }
        else {
            document.getElementById("new-avatar").style.color = "#f06565";
            document.getElementById("new-avatar").innerHTML = "Only JPG, GIF or PNG";
        }
    }
    else
        document.getElementById("new-avatar").innerHTML = "";

}