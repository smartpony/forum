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