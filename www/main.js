const websocketUrl = "wss://" + window.location.host + "/checkbox/ws"
const checkboxElem = document.getElementById("theCheckbox");
const messageElem = document.getElementById("theMessage");
const socket = new WebSocket(websocketUrl);

var lastTimestamp = 0;

function getElapsedTime(timestamp){
    var res = "";
    var interval = Date.now()/1000 - timestamp;
    var years = Math.floor(interval / 31536000);
    if (years > 1)
        res = years + " years";
    else if (years == 1)
        res = years + " year";
    interval -= years * 31536000;

    var months = Math.floor(interval / 2592000);
    if (months > 1)
        res = months + " months";
    else if (months == 1)
        res = months + " month";
    interval -= months * 2592000;

    var days = Math.floor(interval / 86400);
    if (days > 1)
        res = days + " days";
    else if (days == 1)
        res = days + " day";
    interval -= days * 86400;

    var hours = Math.floor(interval / 3600);
    if (hours > 1)
        res = hours + " hours";
    else if (hours == 1)
        res = hours + " hour";
    interval -= hours * 3600;

    var minutes = Math.floor(interval / 60);
    if (minutes > 1)
        res = minutes + " minutes";
    else if (minutes == 1)
        res = minutes + " minute";

    var seconds = Math.floor(interval - minutes * 60);
    if (seconds > 1)
        res = seconds + " seconds";
    else
        res = seconds + " second";

    return res;
}

function updateMessage(){
    var message;
    if (checkboxElem.checked)
        message = "Checked "
    else
        message = "Unchecked "
    message += getElapsedTime(lastTimestamp) + " ago";
    messageElem.innerHTML = message;
}

socket.addEventListener("message", (event) => {
    console.log("recieved: " + event.data);
    var data = JSON.parse(event.data);
    checkboxElem.checked = data["state"];
    lastTimestamp = data["timestamp"];
    updateMessage();
});

checkboxElem.addEventListener("click", (event) => {
    var message = { "state": checkboxElem.checked };
    socket.send(JSON.stringify(message));
    lastTimestamp = Date.now() / 1000;
    updateMessage();
});

setInterval(updateMessage, 1000);

// Checking current state
socket.onopen = () => {
    socket.send(JSON.stringify({ "ask": "" }))
};
