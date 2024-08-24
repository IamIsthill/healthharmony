import {
    openModal,
    closeModal,
    getCurrentUrl
} from '/static/js/utils.js'

import {
    createViewIllnessBody,
    format_date,
    getIllnessUsingId,
    formatDatesInVisitHistory
} from '/static/js/staff/record-visit.js'

import {
    formatDatesInRequestHistory,
    parseBoolean,
    createRequestBody,
    getFilteredCertificateData
} from '/static/js/staff/record-request.js'

const historyData = JSON.parse(document.getElementById('history-data').textContent)
const certficateChartData = JSON.parse(document.getElementById('certificate-chart').textContent)
const certificates = JSON.parse(document.getElementById('certificates').textContent)
main()

function main() {
    // console.log(historyData)
    // console.log(certficateChartData)
    // console.log(certificates[2])
    // Visit
    listenAddRecordBtn()
    formatDatesInVisitHistory(format_date)
    listenViewIllnessesBtn()
    listenViewPatient()

    //chart
    listenRequestDateBtns()

    //requests
    formatDatesInRequestHistory(format_date)
    listenRequestStatusBtns()

    //pagination links
    listenToLinks()

    createRequestBody(true, certificates, NaN)


}

function listenRequestStatusBtns() {
    const requestStatusBtns = document.querySelectorAll('.js-request-status-filter')
    for (const btn of requestStatusBtns) {
        btn.addEventListener('click', () => {
            const status = parseBoolean(btn.getAttribute('data-filter'))
            const url = getCurrentUrl()
            const certPage = url.searchParams.get('cert-page')
            getFilteredCertificateData(certificates, status, certPage)
            // createRequestBody(status, certificates, certPage)
            // formatDatesInRequestHistory(format_date)

        })
    }
}

function listenRequestDateBtns() {
    const requestDateBtns = document.querySelectorAll('.js-request-date-filter')
    for (const btn of requestDateBtns) {
        btn.addEventListener('click', () => {
            const filter = btn.getAttribute('data-filter')
            const data = certficateChartData[filter]
            console.log(data)
        })

    }
}

function listenToLinks() {
    const links = document.querySelectorAll('.js-links')
    for (const link of links) {
        link.addEventListener('click', (event) => {
            event.preventDefault()
            let newParams = {}
            const baseUrl = window.location.origin
            let newUrl = `${baseUrl}/staff/records/`
            const clickedHref = link.getAttribute('href')
            const clickedUrl = new URL(`${newUrl}${clickedHref}`)
            const clickParams = new URLSearchParams(clickedUrl.search)
            const currentUrl = new URL(window.location.href)
            const currentParams = new URLSearchParams(currentUrl.search)

            for (const [key, value] of currentParams.entries()) {
                newParams[key] = value;
            }

            for (const [key, value] of clickParams.entries()) {
                newParams[key] = value;
            }
            newUrl = new URL(newUrl)
            for (const [key, value] of Object.entries(newParams)) {
                newUrl.searchParams.append(key, value);
            }
            window.location.href = newUrl
        })
    }
}

function listenViewPatient() {
    const viewPatientBtns = document.querySelectorAll('.js-view-patient')
    const baseUrl = window.location.origin
    for (const btn of viewPatientBtns) {
        btn.addEventListener('click', () => {
            const patientId = btn.getAttribute('data-patient-id')
            const url = `${baseUrl}/doctor/patient/${patientId}/`
            window.location.href = new URL(url)
        })
    }
}

function listenViewIllnessesBtn() {
    const viewIllnessBtns = document.querySelectorAll('.js-view-illness-btn')
    for (const viewIllnessBtn of viewIllnessBtns) {
        viewIllnessBtn.addEventListener('click', () => {
            const illnessId = parseInt(viewIllnessBtn.getAttribute('data-illness-id'))
            const illnessData = getIllnessUsingId(historyData, illnessId)
            console.log(illnessData)
            createViewIllnessBody(illnessData)
            const viewIllnessModal = document.getElementById('viewIllnessModal')
            const closeBtns = document.querySelectorAll('.js-close-view-illness-modal')
            openModal(viewIllnessModal)
            for (const btn of closeBtns) {
                closeModal(viewIllnessModal, btn)
            }

        })
    }
}

function listenAddRecordBtn() {
    const addRecordBtn = document.getElementById('addRecordBtn')
    const modal = document.querySelector(".js-add-record-modal")
    addRecordBtn.addEventListener('click', () => {
        openModal(modal)
        const closeBtns = document.querySelectorAll('.js-close-add-record')
        for (const btn of closeBtns) {
            closeModal(modal, btn)
        }

    })
}
