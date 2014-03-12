// --- ФОРМАТИРОВАНИЕ ---------------------------
function selectUserOpen() {
    var dialog_box = document.getElementById('dialogbox');
    var dialog_overlay = document.getElementById('overlay');
    dialog_overlay.style.display = 'block';
    dialog_box.style.display = 'block';
}

function selectUserClose() {
    var dialog_box = document.getElementById('dialogbox');
    var dialog_overlay = document.getElementById('overlay');
    var recepient = document.getElementById('recepient');
    var dialog_select = document.getElementById('dialog_select');
    dialog_overlay.style.display = 'none';
    dialog_box.style.display = 'none';
    recepient.value = dialog_select.value;
}

function selectSearch()
{
    var dialog_select = document.getElementById('dialog_select');
    var dialog_input = document.getElementById('dialog_input');
    var start_with = new RegExp('^'+dialog_input.value+'.*', 'ig');
    for (var i = 0; i <= dialog_select.length; i++) {
        if (dialog_select.options[i].innerHTML.match(start_with) != null) {
            dialog_select.selectedIndex = i;
            break;
        }
    }
}

function selectUser(object)
{
    var dialog_input = document.getElementById('dialog_input');
    dialog_input.value = object.value;
}