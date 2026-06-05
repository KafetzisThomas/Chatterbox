export function sendImage(chatSocket) {
    const file = document.querySelector("#image_input").files[0];
    if (file) {
        const reader = new FileReader();
        reader.onloadend = function () {
            const base64String = reader.result.split(',')[1];
            chatSocket.send(JSON.stringify({
                image: base64String,
                username: document.getElementById('username').value,
            }));
        };
        reader.readAsDataURL(file);
    }
}
