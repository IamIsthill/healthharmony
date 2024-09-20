const btns = document.querySelectorAll('.js-modal-btn-ok')

for (const btn of btns) {
    btn.addEventListener('click', () => {
        const error_modal = document.getElementById('popupError')
        const sucess_modal = document.getElementById('popupSuccess')
        if (error_modal) {
            error_modal.style.display = 'none'

        }
        if (sucess_modal) {
            sucess_modal.style.display = 'none'

        }
    })
}
