document.querySelectorAll('.card-item').forEach(card => {
    const contentWrapper = card.querySelector('.content-wrapper');
    const seeMoreButton = card.querySelector('.see-more');

    // Check if content height exceeds max-height
    if (contentWrapper.scrollHeight <= contentWrapper.clientHeight) {
        seeMoreButton.style.display = 'none'; // Hide the button if content doesn't exceed max-height
    }

    seeMoreButton.addEventListener('click', function() {
        contentWrapper.classList.toggle('expanded');

        if (contentWrapper.classList.contains('expanded')) {
            this.textContent = "See Less";
        } else {
            this.textContent = "See More";
            contentWrapper.scrollTop = 0; // Scroll back to the top when collapsing
        }
    });
});
