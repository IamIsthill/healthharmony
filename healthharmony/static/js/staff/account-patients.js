export function getPatientDataUsingId(patientData, id) {
    const mid = Math.ceil(patientData.length / 2)
    const firstArr = patientData.slice(0, mid)
    const secondArr = patientData.slice(mid)

    for (const patient of firstArr) {
        if (parseInt(patient.id) == parseInt(id)) {
            return patient
        }
    }

    if (secondArr.length > 0) {
        return getPatientDataUsingId(secondArr, id)
    }
    return null
}

export function createPatientInformation(data, x, y, format_date) {
    const hoverHTML = document.createElement('div')
    hoverHTML.className = 'js-hover-patient'
    hoverHTML.style.position = 'absolute';
    let date = ''
    try {
        date = format_date(data.date_joined)
    } catch (error) {
        console.log(error)
    }
    const content = `

        <img src="/media/${data.profile}">
        <p>${data.first_name} ${data.last_name}</p>
        <p>${data.email}</p>
        <hr>
        <p>${data.department_name}</p>
        <p>${date}</p>

    `
    hoverHTML.style.top = `${y+5}px`
    hoverHTML.style.left = `${x+5}px`
    hoverHTML.style.zIndex = '100'
    hoverHTML.innerHTML = content
    document.body.append(hoverHTML)
}

export function checkIfFilterExist(filter) {
    const filterInstances = document.querySelectorAll('.js-patient-filter')
    for (const filterInstance of filterInstances) {
        if (filterInstance.getAttribute('data') == filter) {
            return true
        }
    }
    return false
}

export function getFilterParams(filters) {
    let filterParams = ''
    if (filters.length <= 0) {
        return `
            String(patient.department_name).toLowerCase().includes(searchText) ||
            String(patient.first_name).toLowerCase().includes(searchText) ||
            String(patient.last_name).toLowerCase().includes(searchText)
        `
    }

    for (const filter in filters) {
        if (filters[filter] == 'department') {
            filterParams += `String(patient.department_name).toLowerCase().includes(searchText)`
        }
        if (filters[filter] == 'name') {
            filterParams += `
                String(patient.first_name).toLowerCase().includes(searchText) ||
                String(patient.last_name).toLowerCase().includes(searchText)
            `
        }
        if (filter < filters.length - 1) {
            filterParams += `||`
        }
    }
    return filterParams
}

export function filterPatientData(filterParams, patientData, searchText) {
    searchText = searchText.toLowerCase()

    let filteredPatientData = []
    for (const patient of patientData) {
        if (eval(filterParams)) {
            filteredPatientData.push(patient)
        }
    }
    return filteredPatientData
}

export function getPatientFilter() {
    let filters = []
    const filterInstances = document.querySelectorAll('.js-patient-filter')

    for (const filterInstance of filterInstances) {
        const filter = filterInstance.getAttribute('data')
        filters.push(filter)
    }
    return filters
}

export function updatePatientHTML(filteredPatientData) {
    const patientBody = document.querySelector('.js-patients-body')

    let html = ''

    if (filteredPatientData.length <= 0) {
        html += `
            <tr>
                <td colspan="3">No matching patient data.</td>
            </tr>
        `
    } else {
        for (const item of filteredPatientData) {
            html += `
                <tr>
                    <td class="js-patient-profile" data-patient-id="${item.id}">${item.first_name} ${item.last_name}</td>
                    <td class="js-department-names">${item.department_name}</td>
                    <td class="js-dates">${item.last_visit}</td>
                </tr>
            `
        }
    }

    patientBody.innerHTML = html
}

export function formatDepartmentNames() {
    const departmentNames = document.querySelectorAll('.js-department-names')
    for (const department of departmentNames) {
        const text = department.innerText
        if (text == 'null') {
            department.innerText = ' '
        }

    }
}

export function formatDatesInPatientsPage(format_date) {
    const dates = document.querySelectorAll('.js-dates')
    for (const date of dates) {
        try {
            let formattedDate = format_date(date.innerText)
            if (formattedDate.includes('Invalid Date')) {
                formattedDate = ' '

            }
            date.innerText = formattedDate
        } catch (error) {
            console.error(error)
        }
    }
}


/**UPDATED FUNCTIONS */

// This will get the params based on the current state of the html
export function get_sorted_patient_data_based_on_current_params(patientData) {
    const filter = get_current_patient_sort()
    const direction = get_current_patient_direction()
    const search_text = get_patient_search_text()
    const filtered_patient_data = get_filtered_patient_data(filter, search_text, patientData)
    const sorted_patient_data = get_sorted_patient_data(filter, direction, filtered_patient_data)

    return sorted_patient_data
}

export function update_patient_table(filtered_patient_data, format_date) {
    const patient_table_body = document.querySelector('.js-patients-body')
    patient_table_body.innerHTML = ''

    if (filtered_patient_data.length == 0) {
        const tr_element = document.createElement('tr')
        tr_element.innerHTML = `
        <td class="table-data" colspan="3">No data found</td>
        `
        patient_table_body.appendChild(tr_element)
        return
    }

    for (const patient of filtered_patient_data) {
        const tr_element = document.createElement('tr')
        tr_element.innerHTML = `
            <td class="table-data js-patient-profile" data-patient-id="${patient.id}">${patient.first_name} ${patient.last_name}</td>
            <td  class="table-data js-department-names">${patient.department_name ? patient.department_name : ''}</td>
            <td  class="table-data js-dates">${format_date(patient.last_visit)}</td>
        `
        patient_table_body.appendChild(tr_element)
    }
}

export function create_hover_patient_information(patient_data, x, y, format_date) {
    const hoverHTML = document.createElement('div')
    hoverHTML.className = 'js-hover-patient'
    hoverHTML.style.position = 'absolute'
    let date = ''
    try {
        date = format_date(patient_data.date_joined)
    } catch (error) {
        console.log(error)
    }
    const content = `
        <img src="https://healthharmony-staticfiles.s3.ap-southeast-2.amazonaws.com/${patient_data.profile}">
        <p class="hover-name">${patient_data.first_name} ${patient_data.last_name}</p>
        <p class="hover-email">${patient_data.email}</p>
        <hr>
        <div class = "hover-dep">
        <span> Department </span>
        <p>${patient_data.department_name ? patient_data.department_name : ''}</p>
        </div>
        <div class = "hover-date">
        <span> Date Joined </span>
        <p>${date}</p>
        </div>
    `
    hoverHTML.style.top = `${y + 5}px`
    hoverHTML.style.left = `${x + 5}px`
    hoverHTML.style.zIndex = '100'
    hoverHTML.innerHTML = content
    document.body.append(hoverHTML)
}

export function get_patient_data(patient_datas, patient_id) {
    for (const patient of patient_datas) {
        if (parseInt(patient.id) == parseInt(patient_id)) {
            return patient
        }
    }
    return null
}
/** */


function get_current_patient_sort() {
    const btn = document.querySelector('.js-patient-filter-inputs')
    return btn.value
}

function get_patient_search_text() {
    const search_field = document.querySelector('.js-patient-search-field')
    return search_field.value
}

function get_current_patient_direction() {
    const btn = document.querySelector('.js_patient_direction')
    const direction = btn.getAttribute('data-sort')
    return direction
}

function get_filtered_patient_data(filter, search_text, patientData) {
    let filtered_data = []

    if (filter == '') {
        for (const patient of patientData) {
            if (String(patient.department_name).toLowerCase().includes(search_text) ||
                String(patient.first_name).toLowerCase().includes(search_text) ||
                String(patient.last_name).toLowerCase().includes(search_text)) {
                filtered_data.push(patient)
            }
        }
    } else if (filter == 'name') {
        for (const patient of patientData) {
            if (String(patient.first_name).toLowerCase().includes(search_text) ||
                String(patient.last_name).toLowerCase().includes(search_text)) {
                filtered_data.push(patient)
            }
        }
    } else if (filter == 'department') {
        for (const patient of patientData) {
            if (String(patient.department_name).toLowerCase().includes(search_text)) {
                filtered_data.push(patient)
            }
        }
    }

    return filtered_data
}

function get_sorted_patient_data(filter, direction, patient_data) {
    if (direction == 'asc') {
        if (filter == '') {
            patient_data.sort(
                (a, b) => {
                    let nameA = String(a.last_name).toLowerCase()
                    let nameB = String(b.last_name).toLowerCase()

                    if (nameA < nameB) return -1
                    if (nameA > nameB) return 1
                    return 0
                }
            )
        } else if (filter == 'name') {
            patient_data.sort(
                (a, b) => {
                    let nameA = String(a.first_name).toLowerCase()
                    let nameB = String(b.first_name).toLowerCase()

                    if (nameA < nameB) return -1
                    if (nameA > nameB) return 1
                    return 0
                }
            )
        } else if (filter == 'department') {
            patient_data.sort(
                (a, b) => {
                    let nameA = String(a.department_name).toLowerCase()
                    let nameB = String(b.department_name).toLowerCase()

                    if (nameA < nameB) return -1
                    if (nameA > nameB) return 1
                    return 0
                }
            )
        }
    } else if (direction == 'desc') {
        if (filter == '') {
            patient_data.sort(
                (a, b) => {
                    let nameA = a.last_name.toLowerCase()
                    let nameB = b.last_name.toLowerCase()

                    if (nameA > nameB) return -1
                    if (nameA < nameB) return 1
                    return 0
                }
            )
        } else if (filter == 'name') {
            patient_data.sort(
                (a, b) => {
                    let nameA = String(a.first_name).toLowerCase()
                    let nameB = String(b.first_name).toLowerCase()

                    if (nameA > nameB) return -1
                    if (nameA < nameB) return 1
                    return 0
                }
            )
        } else if (filter == 'department') {
            patient_data.sort(
                (a, b) => {
                    let nameA = String(a.department_name).toLowerCase()
                    let nameB = String(b.department_name).toLowerCase()

                    if (nameA > nameB) return -1
                    if (nameA < nameB) return 1
                    return 0
                }
            )
        }

    }

    return patient_data
}
