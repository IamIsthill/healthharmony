import {
    setSpinner
} from '/static/js/spinner.js'
const illnessData = JSON.parse(document.getElementById('illness_data').textContent)

main()

async function main() {
    const userId = JSON.parse(document.getElementById('userId').textContent)
    const mainContainer = document.querySelector('.container')
    const spinner = document.getElementById('loading-spinner')
    const pageUrl = `/patient/patient-profile/${userId}/`

    setSpinner(mainContainer, spinner, pageUrl)

    filterIllness()
    expandIllness()
    editIllness()
}

function filterIllness() {
    const illnessFilterBtns = document.querySelectorAll('.illness_filter')
    for (const btn of illnessFilterBtns) {
        btn.addEventListener('click', () => {
            const filter = btn.getAttribute('data-category').toLowerCase()
            const data = filterIllnessData(filter)
            createIllnessBody(data)
            expandIllness()
            editIllness()
        })
    }
}

function createIllnessBody(data) {
    const illnessBody = document.querySelector('.illness_body')
    let html = ''
    console.log(data.length)
    if (data.length <= 0) {
        html = '<h5>No visit history</h5>'
    }
    for (const illness of data) {
        let treatmentHTML = ''

        for (const treatment of illness.treatments) {
            treatmentHTML += `
        <li>${treatment.category}: ${treatment.medicine} ${treatment.quantity} ${treatment.unit} </li>
      `
        }

        html += `
      <div data-illness-id="${illness.id}" class="illness">
            <p>Date and Time: ${illness.added}</p>
            <p>Symptoms: ${illness.issue}</p>
            <p>Category: ${illness.category}</p>
            <p>Diagnosis: ${illness.diagnosis}</p>
            <div class="treatment_body hide">
              <p>Treatments:</p>
              <ul>${treatmentHTML}</ul>
            </div>
            <button class="expand-illness">Expand</button>
            <button class="edit-illness">Edit</button>
      </div>
    `
    }
    illnessBody.innerHTML = html
}

function filterIllnessData(filter) {
    const data = illnessData[filter]
    return data
}

function expandIllness() {
    const expandIllnessBtns = document.querySelectorAll('.expand-illness')
    for (const btn of expandIllnessBtns) {
        btn.addEventListener('click', () => {
            const parent = btn.parentElement
            for (const child of parent.childNodes) {
                if (child.nodeType === Node.ELEMENT_NODE && child.classList.contains('treatment_body') && child.classList.contains('hide')) {
                    child.classList.remove('hide')
                    btn.innerHTML = 'Close'
                } else if (child.nodeType === Node.ELEMENT_NODE && child.classList.contains('treatment_body')) {
                    child.classList.add('hide')
                    btn.innerHTML = 'Expand'
                }
            }
        })
    }
}

function editIllness() {
    const editIllnessBtns = document.querySelectorAll('.edit-illness')
    for (const btn of editIllnessBtns) {
        btn.addEventListener('click', () => {
            const parent = btn.parentElement
            const illnessId = parseInt(parent.getAttribute('data-illness-id'))
            const data = getIllnessData(illnessId)
            console.log(data)
        })
    }
}

function getIllnessData(illnessId) {
    let data = null
    for (const illness of illnessData['all']) {
        if (illness.id == illnessId) {
            data = illness
        }
    }
    return data
}
