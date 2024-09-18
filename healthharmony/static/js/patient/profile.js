const user_data = JSON.parse(document.getElementById('user_data').textContent)

console.log(user_data)

/** EDIT PROFILE */
handle_onclick_edit_profile()




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

            // Hide form
            form.setAttribute('style', 'display:none')


        })
    })
}
