import {
    setSpinner
} from '/static/js/spinner.js'

import {
    formatDate,
    openModal,
    closeModal,
    getToken
} from '/static/js/utils.js'
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

    reformatAllDates()
    expandIllness()
    editIllness()
    listenIllnessFilter()
}

function getTreatment(id) {
    let data = []
    for (const treatment of treatmentData) {
        if (parseInt(treatment.inventory_detail) == parseInt(id)) {
            data = treatment
        }
    }
    return data
}

function getFilteredIllnessData(filter) {
    let filteredData = []
    if (filter == 'all') {
        filteredData = illnessesData
    } else {
        for (const illness of illnessesData) {
            if (filter == 'not' && illness.diagnosis == '') {
                filteredData.push(illness)
            } else if (filter == 'done' && illness.diagnosis != '') {
                filteredData.push(illness)
            }
        }
    }
    return filteredData
}

function listenIllnessFilter() {
    const filterBtns = document.querySelectorAll('.js-illness-filter')
    for (const btn of filterBtns) {
        btn.addEventListener('click', () => {
            const filter = btn.getAttribute('data-category')
            const filteredData = getFilteredIllnessData(filter)
            createIllnessBody(filteredData)
            checkAccessToEdit()
            expandIllness()
            editIllness()


        })
    }
}

function createIllnessBody(data) {
    const illnessBody = document.querySelector('.illness_body')
    let html = ''
    if (data.length <= 0) {
        html = '<h5>No visit history</h5>'
    }
    for (const illness of data) {
        let treatmentHTML = ''
        if (illness.diagnosis == '') {
            treatmentHTML += '<button class="js-edit-illness">Edit</button>'
        }
        treatmentHTML += '<button class="js-illness-notes">Leave Notes</button>'
        if (illness.treatment.length > 0) {
            treatmentHTML = `
                <div class="treatment_body hide">
                    <p>Treatments:</p>
                    <ul>
            `
            for (const id of illness.treatment) {
                const treatment = getTreatment(id)
                treatmentHTML += `
                    <li>${treatment.inventory_detail_category}: ${treatment.inventory_detail_name} ${treatment.quantity} ${treatment.inventory_detail_unit} </li>
                `
            }
            treatmentHTML += `
                </ul>
            </div>
            <button class="js-expand-illness">Expand</button>
            `
            if (illness.diagnosis == '') {
                treatmentHTML += `
                    <button class="js-edit-illness">Edit</button>
                `
            }
            treatmentHTML += `
                <button class="js-illness-notes">Leave Notes</button>

            `

        }
        const category = illness.category_name ? illness.category_name : ''

        html += `
      <div data-illness-id="${illness.id}" class="illness">
            <p>Date and Time: ${formatDate(illness.added)}</p>
            <p>Symptoms: ${illness.issue}</p>
            <p>Category: ${category}</p>
            <p>Diagnosis: ${illness.diagnosis}</p>
              ${treatmentHTML}

      </div>
    `
    }
    illnessBody.innerHTML = html
}


function expandIllness() {
    const expandIllnessBtns = document.querySelectorAll('.js-expand-illness')
    for (const btn of expandIllnessBtns) {
        btn.addEventListener('click', () => {
            const parent = btn.parentElement
            for (const child of parent.childNodes) {
                if (child.nodeType === Node.ELEMENT_NODE && child.classList.contains('treatment_body') && child.classList.contains('hide')) {
                    child.classList.remove('hide')
                    btn.innerText = 'Close'
                } else if (child.nodeType === Node.ELEMENT_NODE && child.classList.contains('treatment_body')) {
                    child.classList.add('hide')
                    btn.innerText = 'Expand'
                }
            }
        })
    }
}

async function editIllness() {
    const editIllnessBtns = document.querySelectorAll('.js-edit-illness')
    for (const btn of editIllnessBtns) {
        btn.addEventListener('click', () => {
            const parent = btn.parentElement
            const illnessId = parseInt(parent.getAttribute('data-illness-id'))
            const data = getIllnessUsingId(illnessId, illnessesData)
            updateEditIllnessModal(data)
            listenAddMoreTreatmentField()
            const modal = document.querySelector('.js-edit-illness-modal')
            const closeBtns = document.querySelectorAll('.js-close-btn')
            openModal(modal)
            for (const close of closeBtns) {
                closeModal(modal, close)
            }

        })
    }
}

function reformatAllDates() {
    const dates = document.querySelectorAll('.js-dates')
    for (const date of dates) {
        date.innerText = formatDate(date.textContent)
    }
}

function checkAccessToEdit() {
    if (userAccess < 2) {
        const editBtns = document.querySelectorAll('.js-edit-illness')
        for (const btn of editBtns) {
            btn.remove()
        }
    }
}

function getIllnessUsingId(id, illnessesData) {
    let data = null
    for (const illness of illnessesData) {
        if (parseInt(illness.id) == parseInt(id)){
            data = illness
        }
    }
    return data
}

async function updateEditIllnessModal(illness) {
    const predictedDiagnosis = await fetchPredictedDiagnosis(illness.issue)
    const formBody = document.querySelector('.js-edit-illness-modal .modal-content form')
    formBody.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${getToken()}" /> <input type="hidden" name="illness_id" value="${illness.id}" />`

    let diagnosis = `<input type="text" name="diagnosis" value="${illness.diagnosis}"/>`
    if (illness.diagnosis == '') {
        diagnosis = `<input type="text" name="diagnosis" value="${predictedDiagnosis}"/> <span class="js-clear-diagnosis-btn btn">&times;</span> <span>Note: This is predicted by the system using historical data and may be inaccurate</span>`
    }

    let category = `<input type="text" name="category" value="${illness.category_name}" list="category_list"/>`
    if(illness.category_name == '') {
        console.log('ed')
        category = `<input type="text" name="category" value="" list="category_list"/>`
    }


    let html = `
        <label for="">Symptoms:</label>
        <input type="text" name="issue" value="${illness.issue}"/>
        <label for="">Category:</label>
       ${category}
        <datalist id="category_list">
        </datalist>
        <label for="">Diagnosis:</label>
        ${diagnosis}
        <div>
          <h5>Provide Treatment</h5>
          <div class="js-edit-treatment-list">
          </div>
        </div>

    `
    formBody.innerHTML += html
    updateTreatmentList(illness)
    update_category_html(illness_categories)
    listenAddMoreTreatmentField()
    clear_diagnosis_field()


}

function updateTreatmentList(illness) {
    const treatmentListHtml = document.querySelector('.js-edit-treatment-list')
    let treatments = '<div><input type="text" name="treatment" placeholder="Medicine or Supply.." value="" required/> <input type="number" name="quantity" placeholder="Quantity.." required/><button class="js-edit-add-treatment">Add More Field...</button></div>'
    if (illness.treatment.length > 0) {
        treatments = ''
        const length = parseInt(illness.treatment.length)
        let iter = 0
        for (const id of illness.treatment) {
            const treatment = getTreatment(id)
            const quantity = treatment.quantity ? treatment.quantity : ''
            if (iter == (length - 1)) {
                treatments += `<div><input type="text" name="treatment" placeholder="Medicine or Supply.." value="${treatment.inventory_detail_name}" requires/> <input type="number" name="quantity" placeholder="Quantity.." value="${quantity}" required/> <button class="js-edit-add-treatment">Add More Field...</button></div>`
            } else {
                treatments += `<div><input type="text" name="treatment" placeholder="Medicine or Supply.." value="${treatment.inventory_detail_name}" required/> <input type="number" placeholder="Quantity.." value="${quantity}" name="quantity" required /></div>`
            }
            iter++
        }
    }
    treatmentListHtml.innerHTML = treatments

}

function listenAddMoreTreatmentField() {
    try {
        const addMoreTreatmentFieldBtn = document.querySelector('.js-edit-add-treatment')
        addMoreTreatmentFieldBtn.addEventListener('click', (event) => {
            event.preventDefault()
            let checkFields = true
            const treatment_input_fields = document.querySelectorAll('input[name="treatment"]')
            const quantity_input_fields = document.querySelectorAll('input[name="quantity"]')
            for (const treatment_field of treatment_input_fields) {
                if (!treatment_field.reportValidity()) {
                    checkFields = false
                    break
                }
            }
            for (const quantity_field of quantity_input_fields) {
                if(!quantity_field.reportValidity()) {
                    checkFields = false
                    break
                }
            }
            if (checkFields) {
                addMoreTreatmentFieldBtn.remove()

                const treatment_input = get_treatment_input_element()
                const quantity_input = get_quantity_input_element()
                const add_more_btn = get_add_more_btn ()

                const treatment_div = document.createElement('div')
                treatment_div.appendChild(treatment_input)
                treatment_div.appendChild(quantity_input)
                treatment_div.appendChild(add_more_btn)

                document.querySelector('.js-edit-treatment-list').append(treatment_div)
                listenAddMoreTreatmentField()

            }
        })

    } catch(e) {
        console.error(e.message)
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
        console.error(`Failed to get illness categories: ${error.messages}`)
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
        console.error(`Failed to get illness categories: ${error.messages}`)
        return null
    }
}

function update_category_html(illness_categories) {
    const category_html = document.getElementById('category_list')
    let html = ''
    for (const category of illness_categories) {
        html += `
            <option value="${category.category}">
        `
    }
    category_html.innerHTML = html
}

function clear_diagnosis_field() {
    const btn = document.querySelector('.js-clear-diagnosis-btn')
    btn.addEventListener('click', () => {
        const diagnosis_field = document.querySelector('input[name="diagnosis"]')
        diagnosis_field.value = ''
    })
}

function get_treatment_input_element() {
    const treatment_input = document.createElement('input')
    treatment_input.setAttribute('type', 'text')
    treatment_input.setAttribute('name', 'treatment')
    treatment_input.setAttribute('value', '')
    treatment_input.setAttribute('required', '')
    treatment_input.setAttribute('placeholder', 'Medicine or Supply..')

    return treatment_input
}

function get_quantity_input_element() {
    const quantity_input = document.createElement('input')
    quantity_input.setAttribute('name', 'quantity')
    quantity_input.setAttribute('type', 'number')
    quantity_input.setAttribute('placeholder', 'Quantity...')
    quantity_input.setAttribute('required', '')

    return quantity_input
}

function get_add_more_btn() {
    const add_more_btn = document.createElement('button')
    add_more_btn.classList.add('js-edit-add-treatment')
    add_more_btn.innerText = 'Add More'
    return add_more_btn
}
