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
        <p>Email Address: ${data.email}</p>
        <p>Name: ${data.first_name} ${data.last_name}</p>
        <p>Department: ${data.department_name}</p>
        <p>Joined on: ${date}</p>
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
