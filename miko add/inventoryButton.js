const buttons = document.querySelectorAll('.category-buttons .inventory_cat');

buttons.forEach(button => {
    button.addEventListener('click', () => {
        // Remove the active class from all buttons
        buttons.forEach(btn => btn.classList.remove('active'));

        // Add the active class to the clicked button
        button.classList.add('active');
    });
});
