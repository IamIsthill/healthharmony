import {
    getCurrentUrl,
    paginateArray,
    saveItem,
    getItem,
    removeItem,
    openModal,
    closeModal,
    getToken,
    listenToEnter,
    createChart
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

import {
    getPatientList,
    getDepartment,
    createDeleteDepartmentModal,
    createEditDepartmentModal,
    createViewDepartmentModal,
    getDepartmentLabelsAndCounts

} from '/static/js/staff/account-department.js'

const patientData = JSON.parse(document.getElementById('patientData').textContent)
const departmentData = JSON.parse(document.getElementById('departmentData').textContent)
const employeeData = JSON.parse(document.getElementById('employeeData').textContent)

main()


function main() {
    //patients
    setDefault()
    updatePatientCount()
    checkPatientPagination()
    updatePatientSearchField()
    updatePatientFiltersFromMemory(getItem, updatePatientFilters)
    updatePatientBasedOnSearchFieldAndFilters()
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
    createDepartmentBarGraph()

    //employee
    updateEmployeeHTMl(employeeData)
    console.log(employeeData[1])
    const now = Date.now()
    const oldDate  = new Date(2024, 6, 27, 11, 3, 0).getTime()
    const elapseMilli = now - oldDate

    let stmt = ''

    const seconds = Math.floor(elapseMilli / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    // Remaining hours, minutes, and seconds
    const remainingHours = hours % 24;
    const remainingMinutes = minutes % 60;
    const remainingSeconds = seconds % 60;

    console.log(`Elapsed Time: ${days} days, ${remainingHours} hours, ${remainingMinutes} minutes, and ${remainingSeconds} seconds`);

}

function getElapsedTime() {
    const now = Date.now()
}

function updateEmployeeHTMl(employeeData) {
    const employeeBody = document.querySelector('.js-employee-body')
    let html = ''

    for (const employee of employeeData) {
        let count = 0
        let position = ''
        if (employee.access == 2) {
            count = employee.staff_count
            position = 'Staff'
        }

        if (employee.access == 3) {
            count = employee.doctor_count
            position = 'Doctor'
        }
        html += `
            <tr>
                <td>${employee.first_name} ${employee.last_name}</td>
                <td>${position}</td>
                <td>${employee.last_case}</td>
                <td>${count}</td>
            </tr>
        `
    }
    employeeBody.innerHTML = html
}

function createDepartmentBarGraph() {
    const canvas = document.getElementById('js-department-bar-canvas')
    const ctx = canvas.getContext('2d')
    const {labels, counts} = getDepartmentLabelsAndCounts(departmentData)
    const chartType = 'bar'
    const chartData = {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: [
            'rgba(255, 99, 132, 0.2)',
            'rgba(255, 159, 64, 0.2)',
            'rgba(255, 205, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(201, 203, 207, 0.2)'
          ],
          borderColor: [
            'rgb(255, 99, 132)',
            'rgb(255, 159, 64)',
            'rgb(255, 205, 86)',
            'rgb(75, 192, 192)',
            'rgb(54, 162, 235)',
            'rgb(153, 102, 255)',
            'rgb(201, 203, 207)'
          ],
          borderWidth: 1
        }]
    }

    const chartOptions = {
        plugins: {
            legend: {
                display: false,
                labels: {
                    font: {
                        family: 'Poppins', // Your custom font family
                        size: 14, // Font size
                        weight: 'normal', // Font weight
                        style: 'normal' // Font style
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false // This removes the grid lines on the x-axis
                },
                ticks: {
                    font: {
                        family: 'Arial', // Web-safe font
                        size: 10,
                        weight: 'bold',
                        style: 'normal'
                    }
                }
            },
            y: {
                beginAtZero: true, // Ensure y-axis starts from 0
                display: false
            }
        }
    }
    createChart(ctx, chartType, chartData, chartOptions)
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

function listenDepartmentDelete() {
    const departmentDeleteBtns = document.querySelectorAll('.js-delete-department')
    for (const btn of departmentDeleteBtns) {
        btn.addEventListener('click', () => {
            const departmentId = parseInt(btn.parentElement.getAttribute('data-department-id'))
            const department = getDepartment(departmentData, departmentId)
            createDeleteDepartmentModal(department, getToken)
            const modal = document.querySelector('.js-delete-department-modal')
            const closeBtns = document.querySelectorAll('.js-close-delete-department-modal')
            openModal(modal)
            for (const close of closeBtns) {
                closeModal(modal, close)
            }
        })
    }
}

function listenDepartmentView() {
    const departmentViewBtns = document.querySelectorAll('.js-view-department')
    for (const btn of departmentViewBtns) {
        btn.addEventListener('click', () => {
            const departmentId = parseInt(btn.parentElement.getAttribute('data-department-id'))
            const department = getDepartment(departmentData, departmentId)
            const patients = getPatientList(patientData, departmentId)
            createViewDepartmentModal(department, patients, format_date)
            const modal = document.querySelector('.js-view-department-modal')
            const closeBtns = document.querySelectorAll('.js-close-view-department-modal')
            openModal(modal)
            for (const close of closeBtns) {
                closeModal(modal, close)
            }
        })
    }
}

function listenDepartmentEdit() {
    const departmentEditBtns = document.querySelectorAll('.js-edit-department')
    for (const btn of departmentEditBtns) {
        btn.addEventListener('click', () => {
            const departmentId = parseInt(btn.parentElement.getAttribute('data-department-id'))
            const department = getDepartment(departmentData, departmentId)
            createEditDepartmentModal(department, getToken)
            const modal = document.querySelector('.js-edit-department-modal')
            const closeBtns = document.querySelectorAll('.js-close-edit-department-modal')
            openModal(modal)
            for (const close of closeBtns) {
                closeModal(modal, close)
            }
        })
    }
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
    patientSearchField.addEventListener('mouseenter', () => listenToEnter(updatePatientBasedOnSearchFieldAndFilters))
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

        patient.addEventListener('click', () =>{
            const patientId = parseInt(patient.getAttribute('data-patient-id'))
            const currentUrl = getCurrentUrl()
            const goTo = `/patient/patient-profile/${patientId}/`
            currentUrl.pathname = goTo
            currentUrl.search = ''
            window.location.href = currentUrl.href
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
