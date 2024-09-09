import {
    setSpinner
} from '/static/js/spinner.js'

import {
    formatDate,
    openModal,
    closeModal,
    getToken
} from '/static/js/utils.js'

import {
    get_filtered_illnesses_data,
    get_expand_btn,
    get_edit_btn,
    get_leave_notes_btn,
} from '/static/js/doctor/patient-history.js'
const userId = JSON.parse(document.getElementById('userId').textContent)
const userAccess = JSON.parse(document.getElementById('userAccess').textContent)
const illnessesData = JSON.parse(document.getElementById('illnessData').textContent)
const treatmentData = JSON.parse(document.getElementById('treatmentData').textContent)
const illness_categories = await fetch_illness_categories()
const inventory_list = await fetch_inventory_list()




main()

async function main() {
    const mainContainer = document.querySelector('.container')
    const spinner = document.getElementById('loading-spinner')
    const pageUrl = `/doctor/patient/${userId}/`

    setSpinner(mainContainer, spinner, pageUrl)

    /** TEST AREA */
    console.log(illness_categories)
    console.log(illnessesData)
    console.log(inventory_list)
    console.log(treatmentData)
    console.log(userAccess)
    let predict = await fetchPredictedDiagnosis(illnessesData[0].issue)
    predict = predict ? predict : ''
    console.log(predict)


    filter_visit_history()
    click_expand_show_treatments()

}

function filter_visit_history() {
    const filterBtns = document.querySelectorAll('.js-illness-filter')

    for (const btn of filterBtns) {
        btn.addEventListener('click', () => {
            const filter = btn.getAttribute('data-category')
            const filtered_illness_data = get_filtered_illnesses_data(illnessesData, filter)

            update_visit_html_after_filter(filtered_illness_data)
            click_expand_show_treatments()
        })
    }
}

function click_edit_show_form() {
    const edit_btns = document.querySelectorAll('.js-edit-illness-btn')

}

function click_expand_show_treatments() {
    const expand_btns = document.querySelectorAll('.js-expand-illness-btn')

    if (expand_btns.length > 0) {
        for (const btn of expand_btns) {
            btn.addEventListener('click', () => {
                if(btn.innerText == 'Expand') {
                    const treatment_list = document.querySelector('.js-treatment-list')
                    treatment_list.classList.remove('hide')
                    btn.innerText = 'Close'
                }

                else if(btn.innerText == 'Close') {
                    const treatment_list = document.querySelector('.js-treatment-list')
                    treatment_list.classList.add('hide')
                    btn.innerText = 'Expand'
                }
            })

        }
    }
}

function update_visit_html_after_filter(filtered_illness_data) {
    const illness_history_html = document.querySelector('.illness_body')
    illness_history_html.innerHTML = ''
    if (filtered_illness_data.length == 0) {
        illness_history_html.innerHTML = '<h4>No visit history on this category</h4>'
    } else {
        for (const illness of filtered_illness_data) {
            const illness_div = document.createElement('div')
            illness_div.setAttribute('data-illness-id', illness.id)
            illness_div.classList.add('js-illness')

            const illness_div_body = `
                <p>Date of Visit: ${formatDate(illness.added)}</p>
                <p>Symptoms: ${illness.issue}</p>
                <p>Diagnosis: ${illness.diagnosis ? illness.diagnosis : ''}</p>
            `
            illness_div.innerHTML = illness_div_body

            if (illness.treatment.length > 0) {
                const treatment_div = document.createElement('div')
                treatment_div.classList.add('js-treatment-list hide')
                illness_div.appendChild(treatment_div)

                const expand_btn = get_expand_btn()
                illness_div.appendChild(expand_btn)
            }

            if (userAccess >= 3) {
                const edit_btn = get_edit_btn()
                illness_div.appendChild(edit_btn)
            }

            const note_btn = get_leave_notes_btn()
            illness_div.appendChild(note_btn)

            illness_history_html.appendChild(illness_div)
        }
    }
}

async function fetchPredictedDiagnosis(issue) {
    try {
        let baseUrl = window.location.origin;
        let url = new URL(`${baseUrl}/doctor/get-diagnosis/`);

        if (issue) {
            url.searchParams.append("issue", issue);
        }
        const options = {
            method: "GET",
        };

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    } catch (err) {
        console.error(`Failed to fetch session: ${err.message}`);
        return null;
    }
}

async function fetch_illness_categories() {
    try {
        const baseUrl = window.location.origin
        const url = new URL(`${baseUrl}/doctor/get_illness_categories`)
        const options = {
            method: "GET"
        }
        const response = await fetch(url, options)
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();

    } catch (error) {
        console.error(`Failed to get illness categories: ${error.message}`)
        return null
    }
}

async function fetch_inventory_list() {
    try {
        const baseUrl = window.location.origin
        const url = new URL(`${baseUrl}/doctor/get_inventory_list/`)
        const options = {
            method: "GET"
        }
        const response = await fetch(url, options)
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();

    } catch (error) {
        console.error(`Failed to get illness categories: ${error.message}`)
        return null
    }
}
