handle_onclick_ok_modal()
remove_error_show()
handle_notif()

// Close modal
function handle_onclick_ok_modal() {
    const btns = document.querySelectorAll('.js-modal-btn-ok')

    if (btns.length == 0) {
        return
    }

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
}

// WHen error shows, remove after few seconds
function remove_error_show() {
    const error_elements = document.querySelectorAll('.errorlist')

    if (error_elements.length == 0) {
        return
    }

    for (const element of error_elements) {
        setTimeout(() => {
            element.remove()
        }, 4000)
    }
}

function handle_notif() {
    const messages = document.querySelectorAll('.js-messages')

    if (messages.length <= 0) {
        return
    }

    for (const message of messages) {
        setTimeout(() => {
            message.remove()
        }, 3000)
    }

    const close_btns = document.querySelectorAll('.js-close-messages')

    if (close_btns.length > 0) {
        for (const close of close_btns) {
            close.addEventListener('click', () => {
                close.parentElement.remove()
            })
        }
    }


}
