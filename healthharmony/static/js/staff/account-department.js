export function getPatientList(patientData, departmentId) {
    let data = []
    for (const patient of patientData) {
        if (parseInt(patient.department) == parseInt(departmentId)) {
            data.push(patient)
        }
    }
    return data
}

export function getDepartment(departmentData, deparmentId) {
    let data = null
    for (const department of departmentData) {
        if (parseInt(department.id) == parseInt(deparmentId)) {
            data = department
        }
    }
    return data
}

export function createDeleteDepartmentModal(department, getToken) {
    const formBody = document.querySelector('.js-delete-department-modal .modal-content .form-body')
    const url = `/staff/patient-and-accounts/delete-department/${department.id}/`
    formBody.setAttribute('action', url)
    const token = getToken()
    const html = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${token}" />
        <h2>Confirm delete?</h2>
        <h1>${department.department}</h1>
        <button type="submit">Confirm</button>
        <button type="button" class="js-close-delete-department-modal">Cancel</button
    `
    formBody.innerHTML = html
}

export function createEditDepartmentModal(department, getToken) {
    const token = getToken()
    const formBody = document.querySelector('.js-edit-department-modal .modal-content .form-body')
    const url = `/staff/patient-and-accounts/edit-department/${department.id}/`
    formBody.setAttribute('action', url)
    formBody.reset()
    const html = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${token}" />
        <input type="text" value="${department.department}" name="department_name"required/>
        <button type="submit">Update</button>
        <button type="button" class="js-close-edit-department-modal">Cancel</button>
    `
    formBody.innerHTML = html
}

export function createViewDepartmentModal(department, patients, format_date) {
    const modalContent = document.querySelector('.js-view-department-modal .modal-content')
    let html = `
        <span class="js-close-view-department-modal">&times;</span>
        <h2>${department.department}</h2>
        <h5>As of today, ${department.department} has ${department.count} user(s).</h5>
    `
    if (department.count > 0) {
        html += '<div> <h3>Users</h3>'
        for (const patient of patients) {
            html += `
                <div>
                    <img src="/media/${patient.profile}">
                    <a href="/doctor/patient/${patient.id}/">Go to Profile</a>
                    <p>Name: ${patient.first_name} ${patient.last_name}</p>
                    <p>Email: ${patient.email}</p>
                    <p class="js-dates">Joined On: ${format_date(patient.date_joined)}</p>
                </div>
            `
        }
        html += '</div>'
    }
    modalContent.innerHTML = html
}

export function getDepartmentLabelsAndCounts(departmentData) {
    let labels = []
    let counts = []

    for (const department of departmentData) {
        labels.push(department.department)
        counts.push(department.count)
    }

    return {
        labels,
        counts
    }
}

// Updated functions
export function update_department_table(filtered_department_data, format_date) {
    const department_body_element = document.querySelector('.js_department_body')
    department_body_element.innerHTML = ''

    if (filtered_department_data.length == 0) {
        const department_tr_element = document.createElement('tr')
        department_tr_element.innerHTML = `
            <td class="table-data" colspan="3">No data found</td>
        `
        department_body_element.appendChild(department_tr_element)
        return
    }

    for (const department_data of filtered_department_data) {
        const department_tr_element = document.createElement('tr')
        department_tr_element.setAttribute('data-department-id', department_data.id)

        department_tr_element.innerHTML = `
            <td class="table-data">${department_data.department}</td>
            <td class="table-data js-department-counts">${department_data.count}</td>
            <td class="table-data js-dates">${format_date(department_data.last_department_visit)}</td>
            <td class="table-data js-edit-department btn">Edit</td>
            <td class="table-data js-delete-department btn">Delete</td>
            <td class="table-data js-view-department btn">View</td>
        `

        department_body_element.appendChild(department_tr_element)
    }
}

export function get_sorted_department_data_using_current_params(departmentData) {
    const filter = get_current_department_sort()
    const search_text = get_department_search_text()
    const direction = get_current_department_direction()
    const filtered_department_data = get_filtered_department_data(filter, search_text, departmentData)
    const sorted_department_data = get_sorted_patient_data(filter, direction, filtered_department_data)
    return sorted_department_data
}

function get_current_department_sort() {
    const btn = document.querySelector('.js-department-filter-inputs')
    return btn.value
}

function get_department_search_text() {
    const search_field = document.querySelector('.js-department-search-container')
    return search_field.value
}

function get_current_department_direction() {
    const btn = document.querySelector('.js_department_direction')
    const direction = btn.getAttribute('data-sort')
    return direction
}

function get_filtered_department_data(filter, search_text, departmentData) {
    let filtered_data = []

    if (filter == '') {
        for (const department of departmentData) {
            if (String(department.department).toLowerCase().includes(search_text) ||
                String(department.count).toLowerCase().includes(search_text)) {
                filtered_data.push(department)
            }
        }
    } else if (filter == 'department') {
        for (const department of departmentData) {
            if (
                String(department.department).toLowerCase().includes(search_text)
            ) {
                filtered_data.push(department)
            }
        }
    } else if (filter == 'users') {
        for (const department of departmentData) {
            if (String(department.count).toLowerCase().includes(search_text)) {
                filtered_data.push(department)
            }
        }
    }
    return filtered_data
}

function get_sorted_patient_data(filter, direction, department_data) {
    if (direction == 'asc') {
        if (filter == '' || filter == 'department') {
            department_data.sort(
                (a, b) => {
                    let nameA = String(a.department).toLowerCase()
                    let nameB = String(b.department).toLowerCase()

                    if (nameA < nameB) return -1
                    if (nameA > nameB) return 1
                    return 0
                }
            )
        } else if (filter == 'users') {
            department_data.sort(
                (a, b) => {
                    let nameA = parseInt(a.count)
                    let nameB = parseInt(b.count)

                    if (nameA < nameB) return -1
                    if (nameA > nameB) return 1
                    return 0
                }
            )
        }
    } else if (direction == 'desc') {
        if (filter == '' || filter == 'department') {
            department_data.sort(
                (a, b) => {
                    let nameA = String(a.department).toLowerCase()
                    let nameB = String(b.department).toLowerCase()

                    if (nameA > nameB) return -1
                    if (nameA < nameB) return 1
                    return 0
                }
            )
        } else if (filter == 'users') {
            department_data.sort(
                (a, b) => {
                    let nameA = parseInt(a.count)
                    let nameB = parseInt(b.count)

                    if (nameA > nameB) return -1
                    if (nameA < nameB) return 1
                    return 0
                }
            )
        }
    }

    return department_data
}
