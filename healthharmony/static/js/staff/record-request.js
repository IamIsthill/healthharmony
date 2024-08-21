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

export function createRequestBody(status, certificates, certPage) {
    if (certPage === NaN) {
        certPage = 1
    }
    const requestBody = document.querySelector('.js-request-body')
    let html = ''
    let pages = certPage * 10
    let page = 1
    for (const certificate of certificates) {
        if (page > pages) {
            break
        }
        if (page < (pages - 9)) {
            continue
        }
        let data = null
        if (status == null) {
            data = certificate
        } else if (certificate.released === status) {
            data = certificate
        } else {
            continue
        }

        html += `
            <tr>
                <td>${data.email}</td>
                <td>${data.first_name} ${data.last_name}</td>
                <td>${data.purpose}</td>
                <td class="js-cert-date">${data.requested}</td>
            </tr>
        `
        page++
    }
    requestBody.innerHTML = html
}

export function getFilteredCertificateData(certificates, status, certPage) {
    certPage = parseInt(certPage)
    if (certPage === NaN) {
        certPage = 1
    }
    let pages = certPage * 10
    const pageStart = pages - 11
    const pageEnd = pages - 1
    let data = []
    for (const cert of certificates) {
        if (cert.released == status) {
            data.push(cert)
        }
    }


}
