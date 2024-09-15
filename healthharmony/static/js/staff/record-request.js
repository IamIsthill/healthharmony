export function formatDatesInRequestHistory(format_date) {
    const dateStrings = document.querySelectorAll('.js-cert-date')
    for (const date of dateStrings) {
        const newDate = format_date(date.textContent)
        date.innerText = newDate
    }
}

export function parseBoolean(str) {
    if (!str) {
        return null
    }
    return str.toLowerCase() === 'true';
}

export function createRequestBody(certificates) {
    const requestBody = document.querySelector('.js-request-body')
    let html = ''
    for (const certificate of certificates) {
        let purpose = certificate.purpose
        if (purpose.length > 60) {
            purpose = `${purpose.slice(0, 59)}...`
        }
        let status = ''
        let action = ''

        if ((!certificate.is_ready) && (!certificate.released)) {
            status = '<td class="table-data">Request to be processed</td>'
            action = `<td class="table-data"><button>Mark as Ready</button></td>`
        }
        else if ((certificate.is_ready )&&  (!certificate.released)) {
            status = '<td class="table-data">Ready, waiting to be collected</td>'
            action = `<td class="table-data"><button>Mark as Collected</button></td>`
        }
        else if ((certificate.is_ready) && (certificate.released)) {
            status = `<td class="table-data">Medical certificate was collected</td>`
            action = `<td class="table-data">No actions to be taken</td>`
        }


        html += `
            <tr>
                <td>${certificate.email}</td>
                <td>${certificate.first_name ? certificate.first_name : ''} ${certificate.last_name ? certificate.last_name : ''}</td>
                <td>${purpose}</td>
                <td class="js-cert-date">${certificate.requested}</td>
                ${status}
                ${action}
            </tr>
        `
    }
    requestBody.innerHTML = html
}

export function getFilteredCertificateData(certificates, status, certPage) {
    if (!certPage) {
        certPage = 1
    }
    certPage = parseInt(certPage)
    let data = []
    for (let key in certificates) {
        key = parseInt(key)
        const certificate = certificates[key]
        if (certificate.released == status || status == null) {
            data.push(certificate)
        }
    }

    let itemStart = certPage * 10 - 9
    let itemEnd = certPage * 10
    if (itemStart > data.length) {
        certPage = (Math.ceil(data.length / 10))
        itemStart = certPage * 10 - 9
        itemEnd = certPage * 10
    }

    certificates = []
    for (let key in data) {
        key = parseInt(key)
        if (key + 1 >= itemStart && key + 1 <= itemEnd) (
            certificates.push(data[key])
        )
    }
    return certificates
}
