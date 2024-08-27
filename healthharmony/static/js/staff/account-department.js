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
