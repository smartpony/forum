// Обработка сабмита формы. Если найдены пустые поля - выделить их красным и вернуть false.
function ValidatePostingForm() {
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
    return res;
}

// При вводе данных снимать красное выделение.
function ValidateInput(object) {
  if(object.value != "") {
    object.style.border = "1px solid #abadb3";
    object.style.boxShadow = "";
  }
}