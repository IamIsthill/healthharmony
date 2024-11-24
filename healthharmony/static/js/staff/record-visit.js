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
        <div class = "visit-info-cont">
            <div class = "left-visit"> <h3>Patient Name</h3> </div> <div class = "right-visit"> <h4> ${data.patient_first_name} ${data.patient_last_name}</h4> </div>
        </div>
        <div class = "visit-info-cont">
            <div class = "left-visit"> <h3>Patient's Claim</h3> </div> <div class = "right-visit"> <h4> ${data.issue}</h4> </div>
        </div>
        <div class = "visit-info-cont">
            <div class = "left-visit"> <h3>Illness Category</h3> </div> <div class = "right-visit"> <h4> ${data.category_name ? data.category_name : ''}</h4> </div>
        </div>
        <div class = "visit-info-cont">
            <div class = "left-visit"> <h3>Date and Time of Visit</h3> </div> <div class = "right-visit"> <h4> ${format_date(data.added)}</h4> </div>
        </div>
        <div class = "visit-info-cont">
            <div class = "left-visit"> <h3>Added by</h3> </div> <div class = "right-visit"> <h4> ${data.staff_first_name ? data.staff_first_name : ''}  ${data.staff_last_name ? data.staff_last_name: ''}</h4> </div>
        </div>

    `
    if (data.doctor) {
        html += `
            <h4>Diagnosis: ${data.diagnosis}</h4>
            <h4>Diagnosed by: ${data.doctor}</h4>
            <h4>${treatment}</h4>
        `
    }

    html += '<button class="js-close-view-illness-modal view-cancel-button cancel-btn">Close</button>'
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
            if ((data.diagnosis == '' || !(data.diagnosis)) && (data.patient_first_name.toLowerCase().includes(search
                        .toLowerCase()) || data
                    .patient_last_name.toLowerCase().includes(search.toLowerCase()) || data.issue.toLowerCase()
                    .includes(search
                        .toLowerCase()))) {
                filteredHistoryData.push(data)
            }
        } else if (filter == 2) {
            if ((data.diagnosis != '' && data.diagnosis) && (data.patient_first_name.toLowerCase().includes(search
                        .toLowerCase()) || data
                    .patient_last_name.toLowerCase().includes(search.toLowerCase()) || data.issue.toLowerCase()
                    .includes(search
                        .toLowerCase()))) {
                filteredHistoryData.push(data)
            }
        } else {
            if (data.patient_first_name.toLowerCase().includes(search.toLowerCase()) || data.patient_last_name
                .toLowerCase().includes(
                    search.toLowerCase()) || data.issue.toLowerCase().includes(search.toLowerCase())) {
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
        if (!data.diagnosis || data.diagnosis == '') {
            status = 'Ongoing'
        }
        html += `
            <tr>
                <td class="table-data date date-column" data="date-${data.id}">${formatDate(data.added)}</td>
                <td class="table-data patient-column">${data.patient_first_name} ${data.patient_last_name}</td>
                <td class="table-data concern-column">${issue}</td>
                <td class="table-data status-column ${status=='Finished' ? 'span-green' : 'pending-span'}">${status}</td>
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
