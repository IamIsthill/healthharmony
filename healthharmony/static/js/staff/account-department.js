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
