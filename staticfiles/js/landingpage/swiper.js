let popup = document.getElementById("popup");

function openPopup() {
    try {
        popup.classList.add("open-popup");
    } catch (error) {
        console.error(error.message)

    }
}

function closePopup() {
    try {
        popup.classList.remove("open-popup");
        const baseUrl = new URL(window.location.origin)
        window.location.href = baseUrl
    } catch (error) {
        console.error(error.message)
    }
}

document.addEventListener("DOMContentLoaded", () => {
    openPopup()
})

var swiper = new Swiper(".mySwiper", {
    slidesPerView: 3,
    spaceBetween: 30,
    slidesPerGroup: 3,
    loop: true,
    loopFillGroupWithBlank: true,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
});
