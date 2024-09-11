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
    <div class ="view-data">
        <h4>Date and Time of Visit: ${format_date(data.added)}</h4>
        <h4>Illness Category: ${data.category}</h4>
        <h4>Patient Name: ${data.first_name} ${data.last_name}</h4>
        <h4>Patient's Claim: ${data.issue}</h4>
        <h4>Added by: ${data.staff}</h4>
    </div>
    `
    if (data.doctor) {
        html += `
            <h4>Diagnosis: ${data.diagnosis}</h4>
            <h4>Diagnosed by: ${data.doctor}</h4>
            <h4>${treatment}</h4>
        `
    }

    html += '<button class="js-close-view-illness-modal view-cancel-button cancel-button">Close</button>'
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
