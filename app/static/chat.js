let socket = null;
let typingTimeout = null;
let oldestMessageDate = null;

// =====================
// CONNECT
// =====================
function connect() {
    const chatId = document.getElementById("chatId").value;
    const token = document.getElementById("token").value;

    socket = new WebSocket(`ws://127.0.0.1:8000/ws/${chatId}?token=${token}`);

    socket.onopen = () => {
        log("Connected");
    };

    socket.onmessage = (event) => {
        const eventData = JSON.parse(event.data);

        switch (eventData.type) {

            case "USER_ONLINE":
                log(`🟢 ${eventData.data.user_id} online`);
                break;

            case "USER_OFFLINE":
                log(`🔴 ${eventData.data.user_id} offline`);
                break;

            case "TYPING":
                const typingEl = document.getElementById("typingIndicator");
                typingEl.textContent = eventData.data.is_typing
                    ? `User ${eventData.data.user_id} is typing...`
                    : "";
                break;

            case "HISTORY":
                eventData.data.forEach(msg => {
                    renderMessage(msg, true);

                    if (!oldestMessageDate || msg.created_at < oldestMessageDate) {
                        oldestMessageDate = msg.created_at;
                    }
                });
                break;

            case "TEXT":
                renderMessage(eventData.data);
                break;

            case "FILE":
                renderMessage(eventData.data);
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

    socket.onclose = () => log("Disconnected");
    socket.onerror = (err) => log("Error: " + err);
}

// =====================
// SEND TEXT
// =====================
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

// =====================
// SEND FILE (🔥 окремо!)
// =====================
async function sendFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Select file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // 1. upload
    const res = await fetch("/messages/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (!data.url) {
    alert("Upload failed");
    return;
}

    // 2. send через websocket
    socket.send(JSON.stringify({
        type: "FILE",
        data: {
            url: data.url,
            file_type: data.type
        }
    }));
}

// =====================
// DISCONNECT
// =====================
function disconnect() {
    if (socket) socket.close();
}

// =====================
// UI
// =====================
function log(message) {
    const li = document.createElement("li");
    li.textContent = message;
    document.getElementById("messages").appendChild(li);
}

function renderMessage(msg) {
    const li = document.createElement("li");

    // TEXT
    if (msg.text) {
        li.textContent = `${msg.sender_id}: ${msg.text}`;
    }

    // FILE
    if (msg.file_url) {
        const container = document.createElement("div");

        const sender = document.createElement("div");
        sender.textContent = msg.sender_id;

        container.appendChild(sender);

        //  IMAGE preview
        if (msg.file_type === "IMAGE" || msg.file_type?.startsWith("image")) {
            const img = document.createElement("img");
            img.src = msg.file_url;
            img.style.maxWidth = "200px";
            img.style.display = "block";

            container.appendChild(img);
        } else {
            // 📎 download link
            const link = document.createElement("a");
            link.href = msg.file_url;
            link.textContent = "Download file";
            link.target = "_blank";

            container.appendChild(link);
        }

        li.appendChild(container);
    }

    document.getElementById("messages").appendChild(li);
}

// =====================
// TYPING
// =====================
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("connectBtn").addEventListener("click", connect);

    document.getElementById("messageInput").addEventListener("input", () => {
        if (!socket) return;

        socket.send(JSON.stringify({
            type: "TYPING",
            data: { is_typing: true }
        }));

        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            socket.send(JSON.stringify({
                type: "TYPING",
                data: { is_typing: false }
            }));
        }, 500);
    });
});

// SCROLL EVENT LISTENER
window.addEventListener("scroll", () => {
    if (window.scrollY === 0 && oldestMessageDate) {

        socket.send(JSON.stringify({
            type: "LOAD_MORE",
            data: {
                before: oldestMessageDate
            }
        }));
    }
});
