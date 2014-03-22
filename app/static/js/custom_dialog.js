// --- ДИАЛОГ ВЫБОРА ПОЛЬЗОВАТЕЛЯ ---------------
// Сохранить выбранного пользователя в нужном поле (при закрытии)
function selectUserClose() {
    var dialog_select = document.getElementById('recepient');
    var dialog_select = document.getElementById('dialog-select');
    recepient.value = dialog_select.value;
}

// Выбирать пользователя из списка по ходу ввода
function selectSearch() {
    var dialog_select = document.getElementById('dialog-select');
    var dialog_input = document.getElementById('dialog-input');
    var start_with = new RegExp('^'+dialog_input.value+'.*', 'ig');
    for (var i = 0; i <= dialog_select.length; i++) {
        if (dialog_select.options[i].innerHTML.match(start_with) != null) {
            dialog_select.selectedIndex = i;
            break;
        }
    }
}

// При клике на элемент в списке копировать его в поле ввода
function selectUser(object) {
    var dialog_input = document.getElementById('dialog-input');
    dialog_input.value = object.value;
}