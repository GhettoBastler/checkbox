const websocketUrl = "wss://" + window.location.host + "/checkbox/ws"
const checkboxElem = document.getElementById("theCheckbox");
const socket = new WebSocket(websocketUrl);

socket.addEventListener("message", (event) => {
    console.log("recieved: " + event.data);
    checkboxElem.checked = JSON.parse(event.data)["state"]
});

checkboxElem.addEventListener("click", (event) => {
    var message = { "state": checkboxElem.checked };
    socket.send(JSON.stringify(message));
});

// Checking current state
socket.onopen = () => {
    socket.send(JSON.stringify({ "ask": "" }))
};
