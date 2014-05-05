// --- ВАЛИДАЦИЯ РЕГИСТРАЦИИ --------------------
function regValidate(event) {
    res = true;

    // Введён ли логин + проверка наличия поля
    var $login = $("#login");
    if($login.length && !$login.val()) {
        $login.css({
            "border":"1px solid #f06565",
            "boxShadow":"0 0 1px 1px #f5b3b3"
        });
        res = false;
    }
    // Введён ли email + проверка наличия поля
    var $email = $("#email");
    if($email.length && !$email.val()) {
        $email.css({
            "border":"1px solid #f06565",
            "boxShadow":"0 0 1px 1px #f5b3b3"
        });
        res = false;
    }
    // Введён ли пароль + проверка наличия поля
    var $password = $("#password");
    if($password.length && !$password.val()) {
        $password.css({
            "border":"1px solid #f06565",
            "boxShadow":"0 0 1px 1px #f5b3b3"
        });
        res = false;
    }
    // Правильно ли введено подтверждение пароля + проверка наличия поля
    var $password_confirm = $("#password_confirm");
    var $password_alert = $("#password-alert");
    if($password.length)
        if($password.val() != $password_confirm.val()) {
            $password_alert.show();
            $password_confirm.css({
                "border":"1px solid #f06565",
                "boxShadow":"0 0 1px 1px #f5b3b3"
            });
            res = false;
        }
    return res;
}
// register
$(document).on("submit", "#registration-form", regValidate);

// --- ВАЛИДАЦИЯ ФОРМ ПОСТИНГА ------------------
// Обработка сабмита формы. Если найдены пустые поля - выделить их красным и вернуть false.
function postingFormValidate(event) {
    var res = true;

    // Введён ли текст сообщения + проверка наличия поля для сообщения
    var $message = $("#message");
    if($message.length && !$message.val()) {
        $message.css({
            "border":"1px solid #f06565",
            "boxShadow":"0 0 1px 1px #f5b3b3"
        });
        res = false;
    }
    // Введена ли тема + проверка наличия темы
    var $topic = $("#topic");
    if($topic.length && !$topic.val()) {
        $topic.css({
            "border":"1px solid #f06565",
            "boxShadow":"0 0 1px 1px #f5b3b3"
        });
        res = false;
    }
    // Введён ли адресат сообщения + проверка наличия поля адреса
    var $recepient = $("#recepient");
    if($recepient.length && !$recepient.val()) {
        $recepient.css({
            "border":"1px solid #f06565",
            "boxShadow":"0 0 1px 1px #f5b3b3"
        });
        res = false;
    }
    // Введён ли текст поиска + проверка наличия поля поиска
    var $words = $("#words");
    if($words.length && !$words.val()) {
        $words.css({
            "border":"1px solid #f06565",
            "boxShadow":"0 0 1px 1px #f5b3b3"
        });
        res = false;
    }
    return res;
}
// forum, topic, mail_write
$(document).on("submit", "#posting-form", postingFormValidate);

// --- ВАЛИДАЦИЯ ПРИ РЕДАКТИРОВАНИИ ПРОФИЛЯ -----
// Вывод имени файла выбранного аватара
function showAvatarName(event) {
    source = event.data.source;
    if(source == "hdd")
        var new_avatar = $("#avatar_from_hdd").val();
    else {
        var new_avatar = $("#dialog-input").val();
        $("#avatar_from_inet").val(new_avatar);
    }
    var allowed_ext = ["jpg", "jpeg", "gif", "png"];
    // Исключить полный путь и оставить только имя
    new_avatar = new_avatar.replace(/^.*[\\\/]/, "");

    if(new_avatar) {
        var avatar_ext = new_avatar.split(".").pop().toLowerCase();
        if(allowed_ext.indexOf(avatar_ext) != -1)
            $("#new-avatar").text(new_avatar).css("color", "#505050");
        else
            $("#new-avatar").text("Only JPG, GIF or PNG").css("color", "#f06565");
    }
    else
        $("#new-avatar").text("");
}
// profile_edit
$(document).on("change", "#avatar_from_hdd", {source: "hdd"}, showAvatarName);
$(document).on("click", "#inet-avatar-submit", {source: "inet"}, showAvatarName);

// Выбран ли аватар
function profileFormValidate(event) {
    if($("#new-avatar").text() == "Only JPG, GIF or PNG")
        return false;
    else
        return true;
}
// profile_edit
$(document).on("submit", "#profile-edit-form", profileFormValidate);

// --- ВАЛИДАЦИЯ ФОРМЫ ПОИСКА -------------------
function searchFormValidate(event) {
    var text = $("#words").val();
    var $search_alert = $("#search-alert");
    if(text.length < 4) {
        $search_alert.show();
        return false;
    }
    else
        return true;
}
// search
$(document).on("submit", "#search-form", searchFormValidate);

// --- СНЯТИЕ ВЫДЕЛЕНИЯ -------------------------
function postingFormUnmark(event) {
  if($(this).val())
    $(this).css({
        "border": "1px solid #abadb3",
        "boxShadow": ""
    });
}
// register, forum, topic, mail_write
$(document).on("keyup", "#login, #email, #password, #password_confirm, #topic, #message, #recepient", postingFormUnmark);

// --- ФОРМАТИРОВАНИЕ ---------------------------
// Форматирование текста
function makeFormated(event) {
    tag = event.data.tag;
    // Выбор элемента
    var $textarea = $("#message");
    var text = $textarea.val();
    // Начало и конец выделения
    var start_pos = $textarea.prop("selectionStart");
    var end_pos = $textarea.prop("selectionEnd");
    // Вставка тегов
    // Ссылка
    if(tag == "a")
        edited_text = text.substring(0, start_pos) +
            '[a href="' + text.substring(start_pos, end_pos) + '"]' + 'linkname[/a]' +
            text.substring(end_pos, text.length);
    // Изображение
    else if(tag == "img")
        edited_text = text.substring(0, start_pos) +
            '[img src="' + text.substring(start_pos, end_pos) + '"]' +
            text.substring(end_pos, text.length);
   // Жирный, курсив, подчёркнутый
    else
        edited_text = text.substring(0, start_pos) +
            '[' + tag + ']' + text.substring(start_pos, end_pos) + '[/' + tag + ']' +
            text.substring(end_pos, text.length);
    // Вернуть текст в поле
    $textarea.val(edited_text);
}
// forum, topic, mail_write
$(document).on("click", "#btn-bold", {tag: "b"}, makeFormated);
$(document).on("click", "#btn-italic", {tag: "i"}, makeFormated);
$(document).on("click", "#btn-underlined", {tag: "u"}, makeFormated);
$(document).on("click", "#btn-url", {tag: "url"}, makeFormated);
$(document).on("click", "#btn-image", {tag: "img"}, makeFormated);

// Прозрачность аватара при наведении курсора
 // ???????????????????


// --- ДИАЛОГ ВЫБОРА ПОЛЬЗОВАТЕЛЯ ---------------
// Сохранить выбранного пользователя в нужном поле (при закрытии)
// и вызвать функцию снятия красного выделения
function selectUserClose(event) {
    var $recepient = $('#recepient');
    $recepient.val($('#dialog-select').val());
    $recepient.css({
        "border": "1px solid #abadb3",
        "boxShadow": ""
    });
}
// mail_write
$(document).on("click", "#select-user-submit", selectUserClose);

// Выбирать пользователя из списка по ходу ввода
function selectSearch(event) {
    var start_with = new RegExp('^'+$('#dialog-input').val()+'.*', 'ig');
    $('#dialog-select option').each(function() {
        if (this.text.match(start_with) != null) {
            this.selected = true;
            return false; // аналог break
        }
    });
}
// mail_write
$(document).on("keyup", "#dialog-input", selectSearch);

// При клике на элемент в списке копировать его в поле ввода
function selectUser(event) {
    $('#dialog-input').val($(this).val());
}
// mail_write
$(document).on("click", "#dialog-select", selectUser);