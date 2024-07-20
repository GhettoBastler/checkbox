const websocketUrl = "wss://" + window.location.host + "/checkbox/ws"
const checkboxElem = document.getElementById("theCheckbox");
const messageElem = document.getElementById("theMessage");
const socket = new WebSocket(websocketUrl);

var lastTimestamp;
var lastState;

function formatElapsedTime(interval){
    function euclidianDiv(dividend, divisor){
        var quotient = Math.floor(dividend/divisor);
        var remainder = dividend - divisor * quotient;
        return [quotient, remainder];
    }

    var divisors = [
        [31536000, "year", "years"],
        [2592000, "month", "months"],
        [86400, "day", "days"],
        [3600, "hour", "hours"],
        [60, "minute", "minutes"],
        [1, "second", "seconds"],
    ]

    var quotient;
    for (let i=0; i < divisors.length; i++){
        [quotient, interval] = euclidianDiv(interval, divisors[i][0])
        if (quotient > 0){
            if (quotient == 1)
                return quotient + " " + divisors[i][1];
            else if (quotient > 1)
                return quotient + " " + divisors[i][2];
        }
    }

    return res;
}

function updateMessage(){
    var message = "";
    if (lastTimestamp){
        if (checkboxElem.checked)
            message = "checked";
        else
            message = "unchecked";
        var interval = Date.now()/1000 - lastTimestamp;
        if (interval <= 1){
            message = "just " + message;
            if (checkboxElem.checked != lastState){
                // Flash
                checkboxElem.setAttribute("class", "just");
                messageElem.setAttribute("class", "just");
                setTimeout(() => {
                    messageElem.setAttribute("class", "old");
                    checkboxElem.setAttribute("class", "old");
                }, 1);
            }
        }else{
            message += " " + formatElapsedTime(interval) + " ago";
            messageElem.setAttribute("class", "old");
        }

        message = message.charAt(0).toUpperCase() + message.slice(1);
        lastState = checkboxElem.checked;
    }
    messageElem.innerHTML = message;
}

// Checking current state
socket.onopen = () => {
    socket.addEventListener("message", (event) => {
        console.log("recieved: " + event.data);
        var data = JSON.parse(event.data);
        checkboxElem.checked = data["state"];
        lastTimestamp = data["timestamp"];
        updateMessage();
    });

    checkboxElem.addEventListener("click", (event) => {
        var message = { "type": "set", "state": checkboxElem.checked };
        socket.send(JSON.stringify(message));
        lastTimestamp = Date.now() / 1000;
        updateMessage();
    });

    socket.send(JSON.stringify({ "type": "ask" }))
    setInterval(updateMessage, 1000);
};
