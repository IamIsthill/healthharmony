export function getPatientList(patientData, departmentId) {
    let data = []
    for (const patient of patientData) {
        if(parseInt(patient.department) == parseInt(departmentId)) {
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
    console.log(department)
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
                    <a href="/patient/patient-profile/${patient.id}/">Go to Profile</a>
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
