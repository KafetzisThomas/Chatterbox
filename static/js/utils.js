export function autoScrollMessages() {
    const container = document.getElementById('messages-container');
    container.scroll({
        top: container.scrollHeight,
        behavior: 'smooth'
    });
}

export function convertLinks(text) {
    const urlPattern = /((http|https):\/\/[^\s]+)/g;
    return text.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-white">$1</a>');
}
