let socket = null;

function connect() {
    const chatId = document.getElementById("chatId").value;
    const token = document.getElementById("token").value;

    socket = new WebSocket(`ws://127.0.0.1:8000/ws/${chatId}?token=${token}`);

    socket.onopen = () => {
        log("Connected");
    };

    socket.onmessage = (event) => {
        console.log("RAW:", event.data); // DEBUG

        const eventData = JSON.parse(event.data);

        switch (eventData.type) {

            case "TYPING":
                const typingEl = document.getElementById("typingIndicator");

                if (eventData.data.is_typing) {
                    typingEl.textContent = `User ${eventData.data.user_id} is typing...`;
                } else {
                    typingEl.textContent = "";
                }
                break;

            case "HISTORY":
                eventData.data.forEach(msg => {
                    log(`${msg.sender_id}: ${msg.text}`);
                });
                break;

            case "TEXT":
                log(`${eventData.data.sender_id}: ${eventData.data.text}`);
                break;

            case "JOIN_TO_CHAT":
                log(`User joined: ${eventData.data.user_id}`);
                break;

            case "LEAVE":
                log(`User left: ${eventData.data.user_id}`);
                break;

            default:
                console.log("UNKNOWN EVENT:", eventData);
        }
    };

    socket.onclose = () => {
        log("Disconnected");
    };

    socket.onerror = (err) => {
        log("Error: " + err);
    };
}

function sendMessage() {
    const input = document.getElementById("messageInput");

    socket.send(JSON.stringify({
        type: "TEXT",
        data: {
            text: input.value
        }
    }));

    input.value = "";
}

function disconnect() {
    if (socket) {
        socket.close();
    }
}

function log(message) {
    const li = document.createElement("li");
    li.textContent = message;
    document.getElementById("messages").appendChild(li);
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("connectBtn").addEventListener("click", connect);
});

let typingTimeout = null;

document.getElementById("messageInput").addEventListener("input", () => {
    if (!socket) return;

    // почав друкувати
    socket.send(JSON.stringify({
        type: "TYPING",
        data: {
            is_typing: true
        }
    }));

    // debounce (зупинився друкувати)
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        socket.send(JSON.stringify({
            type: "TYPING",
            data: {
                is_typing: false
            }
        }));
    }, 500);
});
