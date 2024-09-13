const department_data = JSON.parse(document.getElementById('department_data').textContent)
const illness_category_data = JSON.parse(document.getElementById('illness_category_data').textContent)

console.log(department_data)
console.log(illness_category_data)

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
