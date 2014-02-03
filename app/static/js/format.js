// --- ФОРМАТИРОВАНИЕ ---------------------------
function makeFormated(tag) {
    // Выбор элемента
    var textarea = document.getElementById("message");
    // Начало и конец выделения
    var start_pos = textarea.selectionStart;
    var end_pos = textarea.selectionEnd;
    // Вставка тегов
    edited_text = textarea.value.substring(0, start_pos) +
        '[' + tag + ']' + textarea.value.substring(start_pos, end_pos) + '[/' + tag + ']' +
        textarea.value.substring(end_pos, textarea.value.length);
    textarea.value = edited_text;
}

function makeURL() {
    // Выбор элемента
    var textarea = document.getElementById("message");
    // Начало и конец выделения
    var start_pos = textarea.selectionStart;
    var end_pos = textarea.selectionEnd;
    // Вставка тегов
    edited_text = textarea.value.substring(0, start_pos) +
        '[a href="' + textarea.value.substring(start_pos, end_pos) + '"]' + 'linkname[/a]' +
        textarea.value.substring(end_pos, textarea.value.length);
    textarea.value = edited_text;
}

function makeIMG() {
    // Выбор элемента
    var textarea = document.getElementById("message");
    // Начало и конец выделения
    var start_pos = textarea.selectionStart;
    var end_pos = textarea.selectionEnd;
    // Вставка тегов
    edited_text = textarea.value.substring(0, start_pos) +
        '[img src="' + textarea.value.substring(start_pos, end_pos) + '"]' +
        textarea.value.substring(end_pos, textarea.value.length);
    textarea.value = edited_text;
}