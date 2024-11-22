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
    createChart,
    getElapsedTime
} from '../utils.js'

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
} from './account-patients.js'

import {
    getPatientList,
    getDepartment,
    createDeleteDepartmentModal,
    createEditDepartmentModal,
    createViewDepartmentModal,
    getDepartmentLabelsAndCounts,
    update_department_table
} from './account-department.js'

import {
    getEmployeeFilter,
    getEmployeeSearchValue,
    filterEmployeeData
} from './account-clinic.js'

import {
    get_sorted_patient_data_based_on_current_params,
    update_patient_table,
    create_hover_patient_information,
    get_patient_data
} from './account-patients.js'

import {
    get_sorted_department_data_using_current_params,
    update_department_count
} from './account-department.js'

const patientData = JSON.parse(document.getElementById('patientData').textContent)
const departmentData = JSON.parse(document.getElementById('departmentData').textContent)
const employeeData = JSON.parse(document.getElementById('employeeData').textContent)
const static_path = JSON.parse(document.getElementById('static_path').textContent)

main()


function main() {
    /**TEST AREA */

    /**PATIENT TABLE */
    formatDatesInPatientsPage(format_date)
    update_patient_count_element()

    handle_patient_sort()
    handle_click_patient_direction()

    handle_onclick_patient_search()
    handle_onclick_clear_patient_search()
    handle_onhover_patient_search_field()

    handle_onhover_patient_name()
    handle_onclick_patient_name()

    /**DEPARTMENT TABLE */
    update_department_count(departmentData)
    update_department_table(departmentData, format_date)
    handle_onclick_department_direction()
    handle_onclick_department_sort()

    handle_onclick_clear_department_search()
    handle_onclick_department_search()
    handle_onhover_department_search_field()

    listenDepartmentDelete()
    listenDepartmentEdit()
    listenDepartmentView()

    listenAddDepartmentBtn()

    createDepartmentBarGraph()


    /** CLINIC TABLE */
    updateEmployeeHTMl(employeeData)
    handle_onclick_search_employee()
    listenEmployeeFilter()
    listenEmployeeClearBtn()

}

/** MAIN PATIENT FUNCTIONS */

// Update the patient count sa patient table
function update_patient_count_element() {
    const patient_count = patientData.length

    const patient_count_element = document.querySelector('.js-patient-count')
    if (patient_count > 1) {
        patient_count_element.innerText = `Total Patients(${patient_count})`
    } else {
        patient_count_element.innerText = `Total Patient(${patient_count})`

    }
}

// Add "ENTER" key event listener when hovering on patient search field
function handle_onhover_patient_search_field() {
    const search_field = document.querySelector('.js-patient-search-field')

    // This is the logic when  enter key was pressed while the cursor was on hover on patient search field
    const handle_enter_press = (event) => {
        if (event.key == 'Enter') {
            const paginated_data = get_paginated_patient_data()
            const sorted_patient_data = get_sorted_patient_data_based_on_current_params(paginated_data)

            update_patient_table(sorted_patient_data, format_date)
            handle_onhover_patient_name()
            handle_onclick_patient_name()

            // Make sure na ihuli ang pag clear sa search field
            const search_field = document.querySelector('.js-patient-search-field')
            search_field.value = ''
        }
    }

    // When cursor is on search field, add the ENTER key event listener
    search_field.addEventListener('mouseenter', () => {
        document.addEventListener('keypress', handle_enter_press, true)
    })

    // Remove when mouse leaves
    search_field.addEventListener('mouseleave', () => {
        search_field.blur()
        document.removeEventListener('keypress', handle_enter_press, true)
    })
}

// Redirect to doctors patient page when patient name was clicked
function handle_onclick_patient_name() {
    const patient_elements = document.querySelectorAll('.js-patient-profile')

    for (const patient_element of patient_elements) {
        patient_element.addEventListener('click', () => {
            const patient_id = parseInt(patient_element.getAttribute('data-patient-id'))
            const currentUrl = getCurrentUrl()
            const goTo = `/doctor/patient/${patient_id}/`
            currentUrl.pathname = goTo
            currentUrl.search = ''
            window.location.href = currentUrl.href
        })
    }
}

// hovering thingy when pointing your cursor on a patient's name
function handle_onhover_patient_name() {
    const patient_elements = document.querySelectorAll('.js-patient-profile')

    for (const patient_element of patient_elements) {
        patient_element.addEventListener('mouseenter', (event) => {
            const patient_id = parseInt(patient_element.getAttribute('data-patient-id'))
            const patient_data = get_patient_data(patientData, patient_id)

            // Position of cursor
            const x = event.clientX,
                y = event.clientY

            // Create the hovering thingy
            create_hover_patient_information(patient_data, x, y, format_date)

            // Remove hovering when mouse leaves
            patient_element.addEventListener('mouseleave', () => {
                const hover_patient_elements = document.querySelectorAll('.js-hover-patient')

                for (const hover_patient_element of hover_patient_elements) {
                    hover_patient_element.remove()
                }
            })
        })
    }
}

// Lagyan ng listener yung sort like all, department, tapos name
function handle_patient_sort() {
    const btn = document.querySelector('.js-patient-filter-inputs')

    btn.addEventListener('change', () => {
        const paginated_data = get_paginated_patient_data()
        const sorted_patient_data = get_sorted_patient_data_based_on_current_params(paginated_data)

        update_patient_table(sorted_patient_data, format_date)
        handle_onhover_patient_name()
        handle_onclick_patient_name()

    })
}

// Lagyan ng listener yung patient direction like up or down
function handle_click_patient_direction() {
    const btn = document.querySelector('.js_patient_direction')

    btn.addEventListener('click', () => {
        const direction = btn.getAttribute('data-sort')
        if (direction == 'asc') {
            btn.setAttribute('data-sort', 'desc')
        } else if (direction == 'desc') {
            btn.setAttribute('data-sort', 'asc')
        }

        const paginated_data = get_paginated_patient_data()
        const sorted_patient_data = get_sorted_patient_data_based_on_current_params(paginated_data)

        update_patient_table(sorted_patient_data, format_date)
        handle_onhover_patient_name()
        handle_onclick_patient_name()

    })
}

// When pinindot ni user search icon
function handle_onclick_patient_search() {
    const btn = document.querySelector('.js-patient-search-btn')

    btn.addEventListener('click', () => {
        const paginated_data = get_paginated_patient_data()
        const sorted_patient_data = get_sorted_patient_data_based_on_current_params(paginated_data)

        update_patient_table(sorted_patient_data, format_date)
        handle_onhover_patient_name()
        handle_onclick_patient_name()

        // Make sure na ihuli ang pag clear sa search field
        const search_field = document.querySelector('.js-patient-search-field')
        search_field.value = ''
    })
}

// Empty yung search field
function handle_onclick_clear_patient_search() {
    const btn = document.querySelector('.js-patient-clear-btn')

    btn.addEventListener('click', () => {
        const search_field = document.querySelector('.js-patient-search-field')
        search_field.value = ''

        const paginated_data = get_paginated_patient_data()

        update_patient_table(paginated_data, format_date)
        handle_onhover_patient_name()
        handle_onclick_patient_name()

    })
}

function get_paginated_patient_data() {
    const url = getCurrentUrl()
    const page = parseInt(url.searchParams.get('patients-page'))
    const paginated_data = paginateArray(patientData, page)

    return paginated_data
}


/**MAIN DEPARMENT FUNCTIONS */

// When user clicks the arrow/sort btns
function handle_onclick_department_direction() {
    const btn = document.querySelector('.js_department_direction')

    btn.addEventListener('click', () => {
        const direction = btn.getAttribute('data-sort')

        if (direction == 'asc') {
            btn.setAttribute('data-sort', 'desc')
        } else if (direction == 'desc') {
            btn.setAttribute('data-sort', 'asc')
        }

        main_department_table_logic()
    })
}

// When user changes the department filters
function handle_onclick_department_sort() {
    const btn = document.querySelector('.js-department-filter-inputs')

    btn.addEventListener('change', () => {
        main_department_table_logic()
    })
}

// Empty the department search field when user clicks the clear btn
function handle_onclick_clear_department_search() {
    const btn = document.querySelector('.js-department-clear-btn')

    btn.addEventListener('click', () => {
        const search_field = document.querySelector('.js-department-search-container')
        search_field.value = ''

        main_department_table_logic()
    })
}

// Update the html when user clicks the search btn
function handle_onclick_department_search() {
    const btn = document.querySelector('.js-department-search-btn')

    btn.addEventListener('click', () => {
        main_department_table_logic()


        // Make sure na ihuli ang pag clear sa search field
        const search_field = document.querySelector('.js-department-search-container')
        search_field.value = ''
    })
}

// Grouped the logic for updating the department table and reattaching the event listeners
function main_department_table_logic() {
    const filtered_department_data = get_sorted_department_data_using_current_params(departmentData)
    update_department_table(filtered_department_data, format_date)

    listenDepartmentDelete()
    listenDepartmentEdit()
    listenDepartmentView()
}

// Add "ENTER" key event listener when hovering on department search field
function handle_onhover_department_search_field() {
    const search_field = document.querySelector('.js-department-search-container')

    // Actual logic when mouse was on department search field
    const handle_enter_press = (event) => {
        if (event.key == 'Enter') {
            main_department_table_logic()

            // Make sure na ihuli ang pag clear sa search fields
            search_field.value = ''
        }
    }

    search_field.addEventListener('mouseenter', () => {
        document.addEventListener('keypress', handle_enter_press, true)
    })

    // Remove when mouse leaves
    search_field.addEventListener('mouseleave', () => {
        search_field.blur()
        document.removeEventListener('keypress', handle_enter_press, true)
    })
}

/** MAIN CLINIC FUNCTIONS */
function updateEmployeeHTMl(employeeData) {
    const employeeBody = document.querySelector('.js-employee-body')
    let html = ''

    if (employeeData.length == 0) {
        html = `
        <tr>
            <td colspan="4">No Data Found</td>
        </tr>

        `

    } else {



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

            let last_case = ''
            if (employee.last_case) {
                last_case = getElapsedTime(employee.last_case)
            }

            const name = employee.first_name && employee.last_name ? `${employee.first_name} ${employee.last_name}` :
                employee.email
            html += `
            <tr>
                <td class = "table-data">${employee.first_name ? employee.first_name : ''} ${employee.last_name ? employee.last_name : ''}</td>
                <td class = "table-data">${position}</td>
                <td class = "table-data">${last_case}</td>
                <td class = "table-data">${count}</td>
            </tr>
        `
        }
    }
    employeeBody.innerHTML = html
}

function handle_onclick_search_employee() {
    const btn = document.querySelector('.js-employee-search-btn')

    btn.addEventListener('click', () => {
        const search_field = document.querySelector('.js-employee-search-field')
        const search_value = search_field.value.toLowerCase()
        const filter = getEmployeeFilter()
        const filtered_employee_data = filterEmployeeData(employeeData, filter, search_value)
        updateEmployeeHTMl(filtered_employee_data)
    })

}

function listenEmployeeFilter() {
    const employeeFilter = document.querySelector('.js-employee-filters')
    employeeFilter.addEventListener('change', () => {
        const filter = getEmployeeFilter()
        const search_field = document.querySelector('.js-employee-search-field')
        const search_value = search_field.value.toLowerCase()
        const searchedEmployees = filterEmployeeData(employeeData, filter, search_value)
        updateEmployeeHTMl(searchedEmployees)
    })
}



















function click() {
    console.log('click')
}


function listenEmployeeClearBtn() {
    const employeeClearBtn = document.querySelector('.js-employee-clear-btn')
    employeeClearBtn.addEventListener('click', () => {
        document.querySelector('.js-employee-filters').value = ''
        document.querySelector('.js-employee-search-field').value = ''
        updateEmployeeHTMl(employeeData)
    })

}

function enterKeyOnEmployeeSearchField() {
    const filter = getItem('employeeFilter') ? getItem('employeeFilter') : ''
    const searchValue = getItem('employeeSearchValue') ? getItem('employeeSearchValue') : ''
    const searchedEmployees = filterEmployeeData(employeeData, filter, searchValue)
    updateEmployeeHTMl(searchedEmployees)

}

function setEmployeeFilters() {
    const searchValue = getItem('employeeSearchValue') ? getItem('employeeSearchValue') : ''
    const filter = getItem('employeeFilter') ? getItem('employeeFilter') : ''
    document.querySelector('.js-employee-filters').value = filter
    document.querySelector('.js-employee-search-field').value = searchValue
}

function listenEmployeeSearchField() {
    const employeeSearchField = document.querySelector('.js-employee-search-field')
    employeeSearchField.addEventListener('input', () => {
        saveItem('employeeSearchValue', employeeSearchField.value)
    })
    employeeSearchField.addEventListener('mouseenter', () => listenToEnter(enterKeyOnEmployeeSearchField))
}


function listenEmployeeSearchBtn() {
    const employeeSearchBtn = document.querySelector('.js-employee-search-btn')
    employeeSearchBtn.addEventListener('click', () => {
        const filter = getEmployeeFilter()
        const searchValue = getEmployeeSearchValue().toLowerCase()
        const searchedEmployees = filterEmployeeData(employeeData, filter, searchValue)
        updateEmployeeHTMl(searchedEmployees)
    })
}



function createDepartmentBarGraph() {
    const canvas = document.getElementById('js-department-bar-canvas')
    const ctx = canvas.getContext('2d')
    const {
        labels,
        counts
    } = getDepartmentLabelsAndCounts(departmentData)
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
                        family: 'Poppins',
                        size: 14,
                        weight: 'normal',
                        style: 'normal'
                    }
                }
            },
            zoom: {
                pan: {
                    enabled: true,
                    mode: 'x',
                    scaleMode: 'x',

                },
                limits: {
                    x: {
                        min: 0,
                        max: 10000
                    }
                },
                zoom: {
                    mode: 'x',
                    pinch: {
                        enabled: true
                    },
                    drag: {
                        enabled: true,
                        threshold: 50
                    },
                    wheel: {
                        enabled: true,
                        speed: 0.000001
                    }

                    // zoom options and/or events
                }
            }
        },
        // chart js zoom plugin
        transitions: {
            zoom: {
                animation: {
                    duration: 1000,
                    easing: 'easeInOutCubic'
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        family: 'Arial',
                        size: 10,
                        weight: 'bold',
                        style: 'normal'
                    }
                }
            },
            y: {
                beginAtZero: true,
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

function setDefault() {
    try {
        const patientsPagination = document.querySelector('.js-patients-pagination')
        patientsPagination.style.display = "none"
    } catch (e) {
        console.error(e.message)
    }
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
        console.log(patientFilterInput.value)
        // const filter = patientFilterInput.value
        // if (filter) {
        //     if (!checkIfFilterExist(filter)) {
        //         // updatePatientFilters(filter)
        //         const filters = getPatientFilter()
        //         // saveItem('patientFilters', filters)
        //     }
        // }
        // clickToRemovePatientFilter()
    })
}

function clickToRemovePatientFilter() {
    const filterInstances = document.querySelectorAll('.js-patient-filter')
    for (const filterInstance of filterInstances) {
        filterInstance.addEventListener('click', () => {
            filterInstance.remove()
            removeItem('patientFilters')
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
            const x = event.clientX,
                y = event.clientY
            createPatientInformation(data, x, y, format_date)
            patient.classList.add('bordered')

            patient.addEventListener('mouseleave', () => {
                const hoverHTML = document.querySelectorAll('.js-hover-patient')
                for (const html of hoverHTML) {
                    html.remove()
                }
                patient.classList.remove('bordered')
            })
        })

        patient.addEventListener('click', () => {
            const patientId = parseInt(patient.getAttribute('data-patient-id'))
            const currentUrl = getCurrentUrl()
            const goTo = `/doctor/patient/${patientId}/`
            currentUrl.pathname = goTo
            currentUrl.search = ''
            window.location.href = currentUrl.href
        })
    }
}

function format_date(dateString) {
    if (!dateString) {
        return ''
    }
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
    } catch (error) {
        console.error(error.message)
    }
}

function updatePatientCount() {
    const patientCountElement = document.querySelector('.js-patient-count')
    const count = patientData.length
    let content = null
    if (count > 1) {
        content = `All Patients(${count})`
    } else {
        content = `All Patient(${count})`
    }
    patientCountElement.innerText = content
}
