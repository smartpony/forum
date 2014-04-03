// --- ВАЛИДАЦИЯ ФОРМ ПОСТИНГА ------------------
// Обработка сабмита формы. Если найдены пустые поля - выделить их красным и вернуть false.
function PostingFormValidate() {
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

// При вводе данных снимать красное выделение.
function PostingFormUnmark(object) {
  if($(object).val())
    $(object).css({
        "border": "1px solid #abadb3",
        "boxShadow": ""
    });
}


// --- ВАЛИДАЦИЯ ПРИ РЕДАКТИРОВАНИИ ПРОФИЛЯ -----
// Вывод имени выбранного файла аватара
function ShowAvatarName() {
    var new_avatar = $("#avatar").val();
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

// Выбран ли аватар
function ProfileFormValidate() {
    if($("#new-avatar").text() == "Only JPG, GIF or PNG")
        return false;
    else
        return true;
}


// --- ФОРМАТИРОВАНИЕ ---------------------------
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

$(document).on("click", "#btn-bold", {tag: "b"}, makeFormated);
$(document).on("click", "#btn-italic", {tag: "i"}, makeFormated);
$(document).on("click", "#btn-underlined", {tag: "u"}, makeFormated);
$(document).on("click", "#btn-url", {tag: "url"}, makeFormated);
$(document).on("click", "#btn-image", {tag: "img"}, makeFormated);


// --- ДИАЛОГ ВЫБОРА ПОЛЬЗОВАТЕЛЯ ---------------
// Сохранить выбранного пользователя в нужном поле (при закрытии)
// и вызвать функцию снятия красного выделения
function selectUserClose() {
    var $recepient = $('#recepient');
    $recepient.val($('#dialog-select').val());
    PostingFormUnmark($recepient);
}

// Выбирать пользователя из списка по ходу ввода
function selectSearch() {
    var start_with = new RegExp('^'+$('#dialog-input').val()+'.*', 'ig');
    $('#dialog-select option').each(function() {
        if (this.text.match(start_with) != null) {
            this.selected = true;
            return false; // аналог break
        }
    });
}

// При клике на элемент в списке копировать его в поле ввода
function selectUser(object) {
    $('#dialog-input').val($(object).val());
}