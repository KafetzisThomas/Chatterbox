// Import utils and file upload functions
import { convertLinks, autoScrollMessages } from './utils.js';
import { sendImage } from './file_upload.js';

document.addEventListener('DOMContentLoaded', function () {
    setupWebSocketConnection();
    setupMessageInputHandlers();
    autoScrollMessages();
});

function setupWebSocketConnection() {
    const username = document.getElementById('username').value;
    const otherUsername = document.getElementById('otherUsername').value;
    const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${username}/${otherUsername}/`);

    chatSocket.onopen = function (e) {
        console.log("WebSocket connection established.");
    };

    chatSocket.onclose = function (e) {
        console.log("WebSocket connection closed.");
    };

    chatSocket.onmessage = handleIncomingMessage;

    // Attach send message and image handlers
    document.querySelector("#message_send_button").onclick = function (e) {
        sendMessage(chatSocket);
    };

    document.querySelector("#image_send_button").onclick = function (e) {
        document.querySelector("#image_input").click();
    };

    document.querySelector("#image_input").onchange = function (e) {
        sendImage(chatSocket);
    };
}

function setupMessageInputHandlers() {
    const messageInput = document.querySelector("#message_send_input");
    messageInput.focus();
    messageInput.onkeyup = function (e) {
        if (e.keyCode === 13) {
            document.querySelector("#message_send_button").click();
        }
    };
}

function sendMessage(chatSocket) {
    const messageInput = document.querySelector("#message_send_input").value.trim();
    if (messageInput) {
        chatSocket.send(JSON.stringify({
            message: messageInput,
            username: document.getElementById('username').value,
        }));
        document.querySelector("#message_send_input").value = "";
    }
}

function handleIncomingMessage(e) {
    const data = JSON.parse(e.data);
    const div = document.createElement("div");
    const messageContent = convertLinks(data.message);
    const bgColor = data.message && data.message.includes('@') ? 'bg-warning' : '';
    const imageContent = data.image ? `<img src="data:image/png;base64,${data.image}" class="img-fluid rounded mb-1" style="max-width: 200px;"/>` : '';
    div.classList.add("fade-in");

    // Use current time for HH:MM
    const now = new Date();
    const timeString = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'UTC' });

    if (data.username === document.getElementById('username').value) {
        div.classList.add("d-flex", "flex-row", "justify-content-end", "mb-3");
        div.innerHTML = `
            <div>
                ${messageContent ? `<p class="small p-2 me-3 mb-1 rounded-3 bg-primary text-white ${bgColor}">${messageContent}</p>` : ''}
                ${imageContent}
                <p class="small me-3 mb-0 rounded-3 text-muted text-end">${timeString}</p>
            </div>
        `;
    } else {
        div.classList.add("d-flex", "flex-row", "justify-content-start", "mb-3");
        div.innerHTML = `
            <div>
                ${messageContent ? `<p class="small p-2 ms-3 mb-1 rounded-3 bg-secondary text-white ${bgColor}">${messageContent}</p>` : ''}
                ${imageContent}
                <p class="small ms-3 mb-0 rounded-3 text-muted">${timeString}</p>
            </div>
        `;
    }

    document.querySelector("#messages-container").appendChild(div);
    document.querySelector("#messages-container").scrollTop = document.querySelector("#messages-container").scrollHeight;
}
