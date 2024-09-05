export function createViewIllnessBody(data) {
    const modalBody = document.querySelector('#viewIllnessModal .modal-content .modal-body')
    let treatment = ''
    if (data.treatment.length > 0) {
        treatment += '<h4>Treatment:</h4><ul>'
        for (const med of data.treatment) {
            treatment += `
                <li>${med.medicine}: ${med.quantity}</li>
            `
        }
        treatment += '</ul'
    }

    let html = `
        <h4>Date and Time of Visit: ${format_date(data.added)}</h4>
        <h4>Illness Category: ${data.category}</h4>
        <h4>Patient Name: ${data.first_name} ${data.last_name}</h4>
        <h4>Patient's Claim: ${data.issue}</h4>
        <h4>Added by: ${data.staff}</h4>
    `
    if (data.doctor) {
        html += `
            <h4>Diagnosis: ${data.diagnosis}</h4>
            <h4>Diagnosed by: ${data.doctor}</h4>
            <h4>${treatment}</h4>
        `
    }

    html += '<button class="js-close-view-illness-modal">Close</button>'
    modalBody.innerHTML = html
}

export function format_date(dateString) {
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

export function getIllnessUsingId(historyData, id) {
    const mid = parseInt(Math.floor(historyData.length / 2))
    const firstArr = historyData.slice(mid)
    const secondArr = historyData.slice(0, mid)

    for (const data of firstArr) {
        if (parseInt(data.id) == parseInt(id)) {
            return data
        }
    }

    if (secondArr.length > 0) {
        return getIllnessUsingId(secondArr, id)
    }

    return null
}

export function formatDatesInVisitHistory(format_date) {
    const dateStrings = document.querySelectorAll('.date')
    for (const date of dateStrings) {
        const newDate = format_date(date.textContent)
        date.innerText = newDate
    }
}

export function getVisitFilter() {
    const visitFilter = document.querySelector('.js-inventory-category-active')
    return parseInt(visitFilter.getAttribute('data-sorter'))
}

export function getVisitSearchValue() {
    const visitField = document.querySelector('.js-inventory-search-container')
    return visitField.value
}

export function filterHistoryData(historyData, filter, search) {
    let filteredHistoryData = []
    for (const data of historyData) {
        if (filter == 1) {
            if ((data.diagnosis == '') && (data.first_name.toLowerCase().includes(search.toLowerCase()) || data.last_name.toLowerCase().includes(search.toLowerCase()) || data.issue.toLowerCase().includes(search.toLowerCase()))) {
                filteredHistoryData.push(data)
            }
        } else if (filter == 2) {
            if ((data.diagnosis != '') && (data.first_name.toLowerCase().includes(search.toLowerCase()) || data.last_name.toLowerCase().includes(search.toLowerCase()) || data.issue.toLowerCase().includes(search.toLowerCase()))) {
                filteredHistoryData.push(data)
            }
        } else {
            if (data.first_name.toLowerCase().includes(search.toLowerCase()) || data.last_name.toLowerCase().includes(search.toLowerCase()) || data.issue.toLowerCase().includes(search.toLowerCase())) {
                filteredHistoryData.push(data)
            }
        }
    }
    return filteredHistoryData
}

export function createVisitHtml(historyData, formatDate) {
    let html = ''
    for (const data of historyData) {
        let issue = data.issue
        if (issue.length > 60) {
            issue = issue.slice(0, 60)
            issue += '...'
        }
        let status = 'Finished'
        if (data.diagnosis == '') {
            status = 'Ongoing'
        }
        html += `
            <tr>
                <td class="table-data date date-column" data="date-${data.id}">${formatDate(data.added)}</td>
                <td class="table-data patient-column">${data.first_name} ${data.last_name}</td>
                <td class="table-data concern-column">${issue}</td>
                <td class="table-data status-column">${status}</td>
                <td class="table-data view-column js-view-illness-btn"
                    data-illness-id="${data.id}">View Illness</td>
                <td class="table-data profile-column js-view-patient"
                    data-patient-id="${data.patient}">Visit Profile</td>
            </tr>
        `
    }
    if (historyData.length <= 0) {
        html = '<tr><td colspan="6">No available data</td></tr>'
    }
    document.querySelector('.js-visit-history-body').innerHTML = html
}
