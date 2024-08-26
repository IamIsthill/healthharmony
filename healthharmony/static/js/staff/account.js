import {
    getCurrentUrl,
    paginateArray,
    saveItem,
    getItem,
    removeItem,
    openModal,
    closeModal
} from '/static/js/utils.js'

import {
    getPatientDataUsingId,
    createPatientInformation,
    checkIfFilterExist,
    getFilterParams,
    filterPatientData,
    getPatientFilter,
    updatePatientHTML,
    formatDepartmentNames,
    formatDatesInPatientsPage
} from '/static/js/staff/account-patients.js'

const patientData = JSON.parse(document.getElementById('patientData').textContent)
const departmentData = JSON.parse(document.getElementById('departmentData').textContent)

main()


function main() {
    //patients
    setDefault()
    updatePatientCount()
    checkPatientPagination()
    updatePatientSearchField()
    updatePatientFiltersFromMemory(getItem, updatePatientFilters)
    updatePatientBasedOnSearchFieldAndFilters()
    listenToHoverOnPatientName()
    listenToPatientClearBtn()
    listenToHoverOnPatientSearchField()
    listenPatientFilter()
    listenPatientSearchBtn()

    //departments
    formatDepartmentUserCounts()
    listenDepartmentDelete()
    listenDepartmentEdit()
    listenDepartmentView()
    listenAddDepartmentBtn()



}

function listenAddDepartmentBtn() {
    const addDepartmentBtn = document.querySelector('.js-add-department-btn')
    addDepartmentBtn.addEventListener('click', () => {
        const modal = document.querySelector('.js-add-department-modal')
        const form = document.querySelector('.js-add-department-modal .modal-content .form-body')
        const closeBtns = document.querySelectorAll('.js-close-add-department-modal')
        openModal(modal)
        for (const close of closeBtns) {
            form.reset()
            closeModal(modal, close)
        }

    })

}

function getPatientList(patientData, departmentId) {
    let data = []
    for (const patient of patientData) {
        if(parseInt(patient.department) == parseInt(departmentId)) {
            data.push(patient)
        }
    }
    return data
}

function getDepartment(departmentData, deparmentId) {
    let data = null
    for (const department of departmentData) {
        if (parseInt(department.id) == parseInt(deparmentId)) {
            data = department
        }
    }
    return data
}

function listenDepartmentDelete() {
    const departmentDeleteBtns = document.querySelectorAll('.js-delete-department')
    for (const btn of departmentDeleteBtns) {
        btn.addEventListener('click', () => {
            const departmentId = parseInt(btn.parentElement.getAttribute('data-department-id'))
            const deparment = getDepartment(departmentData, departmentId)
            const patients = getPatientList(patientData, departmentId)
            console.log(patients)
        })
    }
}

function listenDepartmentView() {
    const departmentViewBtns = document.querySelectorAll('.js-view-department')
    for (const btn of departmentViewBtns) {
        btn.addEventListener('click', () => {
            const departmentId = parseInt(btn.parentElement.getAttribute('data-department-id'))
            const deparment = getDepartment(departmentData, departmentId)
            const patients = getPatientList(patientData, departmentId)
            console.log(patients)
        })
    }
}

function listenDepartmentEdit() {
    const departmentEditBtns = document.querySelectorAll('.js-edit-department')
    for (const btn of departmentEditBtns) {
        btn.addEventListener('click', () => {
            const departmentId = parseInt(btn.parentElement.getAttribute('data-department-id'))
            const deparment = getDepartment(departmentData, departmentId)
            const patients = getPatientList(patientData, departmentId)
            console.log(patients)
        })
    }
}

function getTokenHTML() {
    const inputs = document.querySelectorAll('input')
    let token = null
    for (const input of inputs) {
        const inputName = input.getAttribute('name')
        if (inputName == 'csrfmiddlewaretoken') {
           token = input
        }
    }
    return token
}

function formatDepartmentUserCounts() {
    const departmentUserCounts = document.querySelectorAll('.js-department-counts')
    for (const count of departmentUserCounts) {
        if (count.innerText.toLowerCase() == 'none') {
            count.innerText = '0'
        }
    }
}

function listenToPatientClearBtn() {
    const patientClearBtn = document.querySelector('.js-patient-clear-btn')
    patientClearBtn.addEventListener('click', () => {
        removeItem('searchItem')
        removeItem('patientFilters')
        document.querySelector('.js-patient-search-field').value = ''
        document.querySelector('.js-patient-filters').innerHTML = ''
        updatePatientBasedOnSearchFieldAndFilters()
    })
}

function updatePatientSearchField() {
    const item = getItem('searchItem')
    if (item) {
        document.querySelector('.js-patient-search-field').value = item
    }
}

function updatePatientFiltersFromMemory(getItem, updatePatientFilters) {
    const filters = getItem('patientFilters')
    if (filters && filters.length > 0) {
        for (const filter of filters) {
            updatePatientFilters(filter)
        }
    }
}

function setDefault(){
    const patientsPagination = document.querySelector('.js-patients-pagination')
    patientsPagination.style.display = "none"
}

function listenPatientSearchBtn() {
    const patientSearchBtn = document.querySelector('.js-patient-search-btn')
    patientSearchBtn.addEventListener('click', () => {
        updatePatientBasedOnSearchFieldAndFilters()
    })
}

function listenToHoverOnPatientSearchField() {
    const patientSearchField = document.querySelector('.js-patient-search-field')
    patientSearchField.addEventListener('mouseenter', listenToEnter)
}

function listenToEnter() {
    document.addEventListener('keypress', (event) => {
        if(event.key == 'Enter') {
            updatePatientBasedOnSearchFieldAndFilters()
        }
    })

}

function updatePatientBasedOnSearchFieldAndFilters() {
    const patientSearchField = document.querySelector('.js-patient-search-field')
    const searchText = patientSearchField.value
    saveItem('searchItem', searchText)
    const filters = getPatientFilter()
    saveItem('patientFilters', filters)
    const filterParams = getFilterParams(filters)
    const filteredPatientData = filterPatientData(filterParams, patientData, searchText)
    const url = getCurrentUrl()
    const page = parseInt(url.searchParams.get('patients-page'))
    const paginatedPatientData = paginateArray(filteredPatientData, page)
    updatePatientHTML(paginatedPatientData)
    formatDatesInPatientsPage(format_date)
    formatDepartmentNames()
    listenToHoverOnPatientName()
    clickToRemovePatientFilter()
}

function listenPatientFilter() {
    const patientFilterInput = document.querySelector('.js-patient-filter-inputs')
    patientFilterInput.addEventListener('change', () => {
        const filter = patientFilterInput.value
        if(filter) {
            if (!checkIfFilterExist(filter)) {
                updatePatientFilters(filter)
                const filters = getPatientFilter()
                saveItem('patientFilters', filters)
            }
        }
        clickToRemovePatientFilter()
    })
}

function clickToRemovePatientFilter() {
    const filterInstances = document.querySelectorAll('.js-patient-filter')
    for (const filterInstance of filterInstances) {
        filterInstance.addEventListener('click', () => {
            filterInstance.remove()
        })
    }
}

function updatePatientFilters(filter) {
    const patientFilters = document.querySelector('.js-patient-filters')
    let filterCollectionHTML = patientFilters.innerHTML
    const filterHTML = `
        <div class="js-patient-filter" data="${filter}">
            <p>${filter.toUpperCase()}  <span class="js-close-button">x</span></p>

        </div>
    `
    filterCollectionHTML += filterHTML
    patientFilters.innerHTML = filterCollectionHTML
}

function listenToHoverOnPatientName() {
    const patients = document.querySelectorAll('.js-patient-profile')
    for (const patient of patients) {
        patient.addEventListener('mouseenter', (event) => {
            const patientId = parseInt(patient.getAttribute('data-patient-id'))
            const data = getPatientDataUsingId(patientData, patientId)
            const x = event.clientX, y = event.clientY
            createPatientInformation(data, x, y, format_date)
            patient.classList.add('bordered')

            patient.addEventListener('mouseleave', () => {
                const hoverHTML = document.querySelectorAll('.js-hover-patient')
                for (const html of hoverHTML){
                    html.remove()
                }
                patient.classList.remove('bordered')
            })
        })
    }
}



function format_date(dateString) {
    const formattedDate = new Date(dateString).toLocaleString("en-US", {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
    });
    return formattedDate
}

function checkPatientPagination() {
    try {
        const patientsPagination = document.querySelector('.js-patients-pagination')
        const count = patientData.length
        if (count > 1) {
            patientsPagination.style.display = "block"
        }
    } catch(error) {
        console.log(error)
    }
}

function updatePatientCount() {
    const patientCountElement = document.querySelector('.js-patient-count')
    const count = patientData.length
    let content = null
    if (count > 1) {
        content = `All Patients(${count})`
    } else {
        content =  `All Patient(${count})`
    }
    patientCountElement.innerText = content
}
