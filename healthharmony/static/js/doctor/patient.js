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
    get_treatment_data_using_id,
    get_illness_data,
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
    // console.log(illness_categories)
    // console.log(illnessesData)
    // console.log(userAccess)
    console.log(inventory_list)
    // console.log(treatmentData)

    /** MAKE HTML PRESENTABLE AND DATA PREPATION*/
    update_existing_dates_to_readable()
    append_category_list(illness_categories)


    filter_visit_history()
    click_expand_show_treatments()
    click_edit_show_form()

}

function click_edit_show_form() {
    const edit_btns = document.querySelectorAll('.js-edit-illness-btn')

    if (edit_btns.length > 0) {
        for (const btn of edit_btns) {
            btn.addEventListener('click', () => {
                const illness_id = btn.parentElement.getAttribute('data-illness-id')
                const illness_data = get_illness_data(illness_id, illnessesData)

                create_illness_edit_form(illness_data)

                const modal = document.querySelector('.js-edit-illness-modal')
                const close_btns = document.querySelectorAll('.js-close-btn')
                openModal(modal)
                for (const close of close_btns) {
                    closeModal(modal, close)
                }
            })
        }
    }
}

function add_more_prescription(inventory_list) {
    const add_more_btn = document.querySelector('.js_add_more_btn')

    add_more_btn.addEventListener('click', (event) => {
        event.preventDefault()
        const inventory_item_elements = document.querySelectorAll('select[name="inventory_item"]')
        const inventory_quantity_elements = document.querySelectorAll('input[name="inventory_quantity"]')
        console.log(is_element_valid(inventory_item_elements) && is_element_valid(inventory_quantity_elements))
        if (
            is_element_valid(inventory_item_elements) &&
            is_element_valid(inventory_quantity_elements)
        ) {
            const treatment_fields = document.querySelector('.js_treatment_fields')
            const container = document.createElement('div')
            const medicine_element = get_medicine_element(inventory_list)
            const quantity_element = get_quantity_element()

            container.append(medicine_element, quantity_element)
            const add_more_btn = document.querySelector('.js_add_more_btn')
            add_more_btn.insertAdjacentElement('beforebegin', container)

            return

            // treatment_fields.append(container, get_add_more_btn())

            // add_more_prescription(inventory_list)
        }
    })
}

function is_element_valid(elements) {
    for (const element of elements) {
        if (!element.reportValidity()) {
            return false
        }
    }
    return true
}

function update_existing_dates_to_readable() {
    const dates = document.querySelectorAll('.js-dates')

    for (const date of dates) {
        date.innerText = formatDate(date.innerText)
    }
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

async function create_illness_edit_form(illness_data) {
    const form_body = document.querySelector('.js-edit-illness-modal form')
    form_body.innerHTML = ''
    const token = getToken()
    form_body.appendChild(get_csrf_element(token))
    form_body.innerHTML += '<label>Symptoms: </label>'
    form_body.appendChild(get_issue_element(illness_data.issue))
    form_body.innerHTML += '<label>Category of Symptoms: </label>'
    form_body.appendChild(get_category_element(illness_data.category_name))

    form_body.innerHTML += '<label>Diagnosis: </label>'
    const diagnosis = await fetchPredictedDiagnosis(illness_data.issue)
    if (illness_data.diagnosis != '' && !diagnosis) {
        form_body.appendChild(get_diagnosis_element(diagnosis))
        form_body.innerHTML += `
            <span class="close js-clear-diagnosis-field">&times;</span>
            <p>This is system generated and may be inaccurate. Please ensure that they are correct.</p>
        `
    } else {
        form_body.appendChild(get_diagnosis_element(illness_data.diagnosis))
    }
    form_body.appendChild(get_treatments_element(illness_data.treatment, inventory_list, treatmentData))

    add_more_prescription(inventory_list)
}

function get_treatments_element(treatments, inventory_list, treatmentData) {
    const treatment_div_element = document.createElement('div')
    treatment_div_element.classList.add('js_treatment_fields')
    treatment_div_element.innerHTML += `<label>Prescriptions: </label>`
    if (treatments.length == 0) {
        const container = document.createElement('div')
        const medicine_element = get_medicine_element(inventory_list)
        const quantity_element = get_quantity_element()

        container.append(medicine_element, quantity_element)
        treatment_div_element.appendChild(container)

    } else {
        for (const id of treatments) {
            const treatment = get_treatment_data_using_id(id, treatmentData)
            const container = document.createElement('div')

            const medicine_element = get_medicine_element(inventory_list)
            medicine_element.setAttribute('value', treatment.inventory_detail_name)

            const quantity_element = get_quantity_element()
            quantity_element.setAttribute('value', treatment.quantity)

            container.append(medicine_element, quantity_element)
            treatment_div_element.appendChild(container)
        }
    }
    const add_more_btn = get_add_more_btn()
    treatment_div_element.appendChild(add_more_btn)

    return treatment_div_element
}

function get_add_more_btn() {
    const add_more_btn = document.createElement('button')
    add_more_btn.classList.add('js_add_more_btn')
    add_more_btn.innerText = 'Add More'

    return add_more_btn
}

function remove_add_more_btn() {
    const add_more_btn = document.querySelector('.js_add_more_btn')
    add_more_btn.remove()
}

function get_medicine_element(inventory_list) {
    const medicine_element = document.createElement('select')
    medicine_element.setAttribute('required', '')
    medicine_element.setAttribute('name', 'inventory_item')

    for (const option of inventory_list) {
        medicine_element.innerHTML += `<option value="${option.item_name}">${option.item_name}</option>`
    }

    return medicine_element
}

function get_quantity_element() {
    const quantity_element = document.createElement('input')
    quantity_element.setAttribute('required', '')
    quantity_element.setAttribute('type', 'number')
    quantity_element.setAttribute('name', 'inventory_quantity')
    quantity_element.setAttribute('placeholder', 'Item quantity...')

    return quantity_element
}

function get_csrf_element(token) {
    const element = document.createElement('input')
    element.setAttribute('name', 'csrfmiddlewaretoken')
    element.value = token
    element.setAttribute('required', '')
    element.setAttribute('type', 'hidden')
    return element
}

function get_issue_element(issue) {
    const element = document.createElement('input')
    element.setAttribute('name', 'issue')
    element.setAttribute('value', issue)
    // element.value = issue
    element.setAttribute('required', '')
    element.setAttribute('type', 'text')
    return element
}

function get_category_element(category) {
    category = category ? category : ''
    const element = document.createElement('input')
    element.setAttribute('name', 'category')
    element.setAttribute('value', category)
    element.setAttribute('required', '')
    element.setAttribute('type', 'text')
    element.setAttribute('list', 'js_categories_list')
    return element
}

function get_diagnosis_element(diagnosis) {
    const element = document.createElement('input')
    element.setAttribute('name', 'diagnosis')
    element.setAttribute('value', diagnosis)
    element.setAttribute('required', '')
    element.setAttribute('type', 'text')
    return element
}

function append_category_list(illness_categories) {
    const form_body = document.querySelector('.js-edit-illness-modal form')
    const element = document.createElement('datalist')
    element.setAttribute('id', 'js_categories_list')
    let html = ''
    for (const category of illness_categories) {
        html += `<option value="${category.category}">`
    }
    element.innerHTML = html
    form_body.insertAdjacentElement('afterend', element)
}

function click_expand_show_treatments() {
    const expand_btns = document.querySelectorAll('.js-expand-illness-btn')

    if (expand_btns.length > 0) {
        for (const btn of expand_btns) {
            btn.addEventListener('click', () => {
                if (btn.innerText == 'Expand') {
                    const treatment_list = document.querySelector('.js-treatment-list')
                    treatment_list.classList.remove('hide')
                    btn.innerText = 'Close'
                } else if (btn.innerText == 'Close') {
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
                <p>Category of Symptoms: ${illness.category_name ? illness.category_name : ''}
                <p>Diagnosis: ${illness.diagnosis ? illness.diagnosis : ''}</p>
            `
            illness_div.innerHTML = illness_div_body

            if (illness.treatment.length > 0) {
                const treatment_div = create_treatment_list(illness.treatment, treatmentData)
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

function create_treatment_list(treatments, treatmentData) {
    const treatment_div = document.createElement('div')
    treatment_div.classList.add('js-treatment-list')
    treatment_div.classList.add('hide')
    treatment_div.innerHTML = '<p>Treatments:</p>'
    let treatment_list_html = ''
    for (const id of treatments) {
        const treatment = get_treatment_data_using_id(id, treatmentData)
        treatment_list_html += `<li>${treatment.inventory_detail_category}: ${treatment.inventory_detail_name} ${treatment.quantity} ${treatment.inventory_detail_unit}</li>`
    }
    treatment_div.innerHTML += treatment_list_html
    return treatment_div
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
