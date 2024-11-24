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

// var swiper = new Swiper(".mySwiper", {
//     slidesPerView: 3,
//     spaceBetween: 30,
//     slidesPerGroup: 3,
//     loop: true,
//     loopFillGroupWithBlank: true,
//     navigation: {
//         nextEl: ".swiper-button-next",
//         prevEl: ".swiper-button-prev",
//     },
// });

var swiper = new Swiper('.mySwiper', {
    slidesPerView: 1,  // How many slides to show at once (1 by default)
    spaceBetween: 10,  // Space between slides in px
    loop: true,        // Enable looping of slides
    loopFillGroupWithBlank: true,
    slidesPerView: 'auto', // Automatically adjust based on content
    centeredSlides: true, // Enable centering
    spaceBetween: 20,
    // Enable responsive breakpoints
    breakpoints: {
        // when window width is >= 640px
        640: {
            slidesPerView: 1,  // Show 1 slide on screens >= 640px
            spaceBetween: 20   // Space between slides in px
        },
        // when window width is >= 768px
        768: {
            slidesPerView: 2,  // Show 2 slides on screens >= 768px
            spaceBetween: 30   // Space between slides in px
        },
        // when window width is >= 1024px
        1024: {
            slidesPerView: 3,  // Show 3 slides on screens >= 1024px
            spaceBetween: 40   // Space between slides in px
        }
    }
});