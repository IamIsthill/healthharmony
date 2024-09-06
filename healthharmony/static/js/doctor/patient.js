import {
    setSpinner
} from '/static/js/spinner.js'

import {
    formatDate
} from '/static/js/utils.js'
const illnessData = JSON.parse(document.getElementById('illness_data').textContent)
const userId = JSON.parse(document.getElementById('userId').textContent)
const userAccess = JSON.parse(document.getElementById('userAccess').textContent)
const illnessesData = JSON.parse(document.getElementById('illnessData').textContent)
const treatmentData = JSON.parse(document.getElementById('treatmentData').textContent)



main()

async function main() {
    const mainContainer = document.querySelector('.container')
    const spinner = document.getElementById('loading-spinner')
    const pageUrl = `/doctor/patient/${userId}/`

    setSpinner(mainContainer, spinner, pageUrl)


    reformatAllDates()
    expandIllness()
    // editIllness()
    listenIllnessFilter()
    console.log(userAccess)
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
            <button class="js-edit-illness">Edit</button>
            `
        }
        const category = illness.category_name ? illness.category_name : ''

        html += `
      <div data-illness-id="${illness.id}" class="illness">
            <p>Date and Time:${formatDate(illness.added)}</p>
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

function editIllness() {
    const editIllnessBtns = document.querySelectorAll('.js-edit-illness')
    for (const btn of editIllnessBtns) {
        btn.addEventListener('click', () => {
            const parent = btn.parentElement
            const illnessId = parseInt(parent.getAttribute('data-illness-id'))
            const data = getIllnessData(illnessId)
            console.log(data)
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
