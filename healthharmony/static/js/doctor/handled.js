
/** CASES TABLE */
handle_onclick_review_btn()

// Redirect when clicking the review button
function handle_onclick_review_btn() {
    const btns = document.querySelectorAll('.js-view-illness')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            const patient_id = btn.getAttribute('data-patient-id')
            const redirect_url = `/doctor/patient/${patient_id}`

            window.location.pathname = redirect_url
        })
    }
}
