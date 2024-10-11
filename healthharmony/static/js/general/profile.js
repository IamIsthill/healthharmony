const profile_path = JSON.parse(document.getElementById('pathname').textContent)

/** EDIT PROFILE */
handle_onclick_edit_profile()

/** RESET PASSWORD */
handle_onclick_reset_pass()

handle_user_upload()

function handle_user_upload() {
    const profile_picture = document.getElementById('profile-picture')

    profile_picture.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.querySelector('.dp-pic').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    })

}



// redirect user to reset view when he wants to reset password
function handle_onclick_reset_pass() {
    const btn = document.querySelector('.js_reset_password')

    btn.addEventListener('click', () => {
        const url = new URL(window.location.href)
        url.pathname = '/accounts/password/reset/'

        window.location.href = url
    })
}

// user click the edit button, show the form
function handle_onclick_edit_profile() {
    const btn = document.querySelector('.js_edit_profile')

    btn.addEventListener('click', () => {
        const form = document.querySelector('.js_profile_form')
        form.setAttribute('style', '')

        const patient_info_element = document.querySelector('.js_patient_info')
        patient_info_element.setAttribute('style', 'display:none')

        const profile_actions_element = document.querySelector('.js_profile_actions')
        profile_actions_element.setAttribute('style', 'display:none')

        // Close the form when user clicks the close button
        const close_btn = document.querySelector('.js_close_profile_form')
        close_btn.addEventListener('click', (event) => {
            event.preventDefault()

            // Display previosly removed elements
            patient_info_element.setAttribute('style', '')
            profile_actions_element.setAttribute('style', '')

            document.querySelector('.dp-pic').src = `${profile_path}`

            // Hide form
            form.setAttribute('style', 'display:none')
        })

        // Limit the number to be typed
        limit_contact_number()
    })
}

function limit_contact_number() {
    const number_input_element = document.querySelector('input[type="number"]')

    number_input_element.addEventListener('input', () => {
        let number = number_input_element.value
        if (number.length > 11) {
            number = number.slice(0, 11)
        }
        number_input_element.value = number
    })
}
