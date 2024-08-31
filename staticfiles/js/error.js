let popup = document.getElementById("popup");

function openPopup() {
    popup.classList.add("open-popup");
}

function closePopup() {
    popup.classList.remove("open-popup");
    const baseUrl = new URL(window.location.href)
    window.location.href = baseUrl
}

document.addEventListener("DOMContentLoaded", () => {
    try {
        openPopup()
    } catch(error) {
        console.error(error)
    }
})
