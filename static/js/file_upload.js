export function sendImage(chatSocket) {
    const file = document.querySelector("#image_input").files[0];
    if (!file) {
        return;
    }

    const username = document.getElementById("username").value;
    const otherUsername = document.getElementById("otherUsername").value;
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const formData = new FormData();
    formData.append("image", file);

    fetch(`/chat/${username}/${otherUsername}/upload_image/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.image_url) {
            chatSocket.send(JSON.stringify({
                username: username,
                image_name: data.image_name,
                image_url: data.image_url,
            }));
        }
    });

    document.querySelector("#image_input").value = "";
}
