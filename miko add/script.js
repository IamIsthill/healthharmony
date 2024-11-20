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

// when user hovers on the info icon on the morbidity bars
function handle_hover_illness_info() {
    const icons = document.querySelectorAll('.js_view_categories')

    // Exit early if there are no icons
    if (icons.length == 0) {
        return
    }



    for (const icon of icons) {
        icon.addEventListener('mouseenter', (event) => {
            const category_id = parseInt(icon.getAttribute('category-id'))

            const category = get_category(category_id)

            // Get cursor location
            const x = event.clientX,
                y = event.clientY

            //Create the hover thingy
            const hover_div = document.createElement('div')
            hover_div.classList.add('js_hover_illness_info')
            hover_div.innerHTML = `
                <h4 class = "hover-title">${category.category}</h4>
                <p class = "hover-info">${category.description}</p>
            `

            // Set design then append to the html
            hover_div.style = `
                position: absolute;
                top: ${y - hover_div.offsetHeight - 5}px; /* Position above the icon */
                left: ${x}px; /* Align with the left edge of the icon */
                z-index: 100;
                background: white;
                border: 1px solid #ccc;
                padding: 8px;
                border-radius: 4px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            `
            document.body.append(hover_div)

            // Remove all hovers when mouse leaves
            icon.addEventListener('mouseleave', () => {
                const hovers = document.querySelectorAll('.js_hover_illness_info')

                for (const hover of hovers) {
                    hover.remove()
                }
            })
        })
    }
}