const static_path = JSON.parse(document.getElementById('static_path').textContent)
const media_path = JSON.parse(document.getElementById('media_path').textContent)

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
        <div class = "delete-illus">
            <img src="${static_path}assets/images/svgs/remove-dep.svg" alt="">
            <h2>Are you sure to delete <span class ="delete-dept">${department.department} Department</span>?</h2>
        </div>
        <div class = "form-buttons delete-buttons">
            <button class = "form-button" type="submit">Confirm</button>
            <button type="button" class="js-close-delete-department-modal cancel-button">Cancel</button>
        </div>
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
        <h1> Change the Department Name </h1>
        <input type="hidden" name="csrfmiddlewaretoken" value="${token}" />
        <div class = "edit-input-cont">
        <span class="material-symbols-outlined">
            domain
        </span>
        <input type="text" value="${department.department}" name="department_name"required/>
        </div>
        <div class = "form-buttons">
            <button class = "form-button edit-button" type="submit">Update</button>
            <button type="button" class="js-close-edit-department-modal cancel-button">Cancel</button>
        </div>
    `
    formBody.innerHTML = html
}

export function createViewDepartmentModal(department, patients, format_date) {
    const modalContent = document.querySelector('.js-view-department-modal .modal-content')
    let html = `
        <span class="material-symbols-outlined close js-close-view-department-modal">cancel</span>
        <div class = "no-account-cont">
        <img src="${static_path}assets/images/svgs/no-account.svg" alt="">
        <h2>${department.department}</h2>
        <h5>This Department has no user.</h5>
        </div>
    `
    if (department.count > 0) {
        html = `
            <span class="material-symbols-outlined close js-close-view-department-modal">cancel</span>
            <div class = "no-account-cont">
            <h2>${department.department}</h2>
            </div>
        `
        html += `
            <div class = "dep-view-cont">
                <h3>Users</h3>
                <div class ="search-container-dep">
                <input type="text" class="js_specific_department_field " placeholder="Search Department...">
                <button class="js_search_specific_department">
                    <span class="material-symbols-outlined">search</span>
                </button>
                </div>
            </div>
            <div class="js_user_list">`
        for (const patient of patients) {
            html += `
                <div class ="department-view">
                    <img src="${media_path}${patient.profile}">
                    <div class = "name-email">
                    <p>${patient.first_name} ${patient.last_name}</p>
                    <p>${patient.email}</p>
                    </div>
                    <a href="/doctor/patient/${patient.id}/">Go to Profile</a>
                </div>
            `
        }
        html += '</div>'
    }
    modalContent.innerHTML = html

    if (department.count > 0) {
        const search_btn = document.querySelector('.js_search_specific_department')
        search_btn.addEventListener('click', () => {
            const search_field = document.querySelector('.js_specific_department_field')
            const search_text = search_field.value.toLowerCase()

            //Search for the user
            let patient_container = []
            if (search_text) {
                for (const patient of patients) {
                    if (String(patient.email).toLowerCase().includes(search_text) ||
                        String(patient.first_name).toLowerCase().includes(search_text) ||
                        String(patient.last_name).toLowerCase().includes(search_text)) {
                        patient_container.push(patient)
                    }
                }
            }

            // Put patient in a div

            let content = "<h1>No User found</h1>" // Default content

            // If may nahanap, default will be changed
            if (patient_container.length > 0) {
                content = ''
                for (const patient of patient_container) {
                    content += `
                    <div class ="department-view">
                        <img src="${media_path}${patient.profile}">
                        <div class = "name-email">
                            <p>${patient.first_name} ${patient.last_name}</p>
                            <p>${patient.email}</p>
                        </div>
                        <a href="/doctor/patient/${patient.id}/">Go to Profile</a>
                    </div>
                    `
                }
            }
            document.querySelector('.js_user_list').innerHTML = content

            // Clean
            search_field.value = ''

        })
    }
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
            <td class="table-data js-edit-department act-data"><span class="btn edit-btn">Edit</span></td>
            <td class="table-data js-delete-department btn"> <span class="btn delete-btn-dept"> Delete </span> </td>
            <td class="table-data js-view-department btn"><span class="btn view-btn">View</span></td>
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

export function update_department_count(departmentData) {
    console.log(departmentData)
    let count = 0
    for (const i of Object.entries(departmentData)) {
        count++
    }
    const text = `Total Department(${count})`
    document.querySelector('.js-department-count').textContent = text

}
