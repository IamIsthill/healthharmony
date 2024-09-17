import {
    openModal,
    closeModal,
    getCurrentUrl,
    getActiveFilter,
    createChart,
    saveItem,
    removeItem,
    getItem,
    formatDate,
    paginateArray,
    getToken,
} from '/static/js/utils.js'

import {
    createViewIllnessBody,
    format_date,
    getIllnessUsingId,
    formatDatesInVisitHistory,
    getVisitFilter,
    getVisitSearchValue,
    filterHistoryData,
    createVisitHtml
} from '/static/js/staff/record-visit.js'

import {
    formatDatesInRequestHistory,
    parseBoolean,
    createRequestBody,
    getFilteredCertificateData
} from '/static/js/staff/record-request.js'

import {
    createRequestBarChart,
    getCountsAndLabelForRequestBar
} from '/static/js/staff/record-bar.js'

const historyData = JSON.parse(document.getElementById('history-data').textContent)
const certficateChartData = JSON.parse(document.getElementById('certificate-chart').textContent)
const certificates = JSON.parse(document.getElementById('certificates').textContent)
main()

function main() {
    //SET PARAMS
    setSavedParams()

    // Visit
    createLogicRequestBarChart()

    listenAddRecordBtn()
    // formatDatesInVisitHistory(format_date)
    listenViewIllnessesBtn()
    listenViewPatient()
    listenVisitFilters()
    listenVisitSearchBtn()
    listenVisitSearchField()

    //chart
    listenRequestDateBtns()

    //requests
    formatDatesInRequestHistory(format_date)
    listenRequestStatusBtns()
    handle_onclick_certificate_action()

    //pagination links
    listenToLinks()

}

// user clicks the action
function handle_onclick_certificate_action() {
    const btns = document.querySelectorAll('.js_certificate_action')
    if (btns.length <= 0) {
        return

    }
    for (const btn of btns) {
        btn.addEventListener('click', () => {
            const certificate_id = btn.getAttribute('data-certificate-id')
            const form = document.createElement('form')
            form.setAttribute('method', 'POST')
            form.setAttribute('action', '')
            form.setAttribute('style', 'display : none')

            const certificate_input_element = document.createElement('input')
            certificate_input_element.setAttribute('value', certificate_id)
            certificate_input_element.setAttribute('type', 'number')
            certificate_input_element.setAttribute('name', 'certificate_id')

            const token_value = getToken()
            const csrf_input_element = document.createElement('input')
            csrf_input_element.setAttribute('type', 'hidden')
            csrf_input_element.setAttribute('value', token_value)
            csrf_input_element.setAttribute('name', 'csrfmiddlewaretoken')

            form.append(certificate_input_element, csrf_input_element)
            document.body.appendChild(form)

            form.submit()

        })
    }
}

// get certificate data using id
function get_certificate_data(id) {
    for (const certificate of certificates) {
        if (parseInt(certificate.id) == parseInt(id)) {
            return certificate
        }
    }
    return null
}



function createLogicRequestBarChart() {
    const filter = getActiveFilter('js-request-date-active', 'data-filter')
    const {
        counts,
        labels
    } = getCountsAndLabelForRequestBar(certficateChartData[filter])
    createRequestBarChart(labels, counts, createChart)
}

function listenRequestStatusBtns() {
    const requestStatusBtns = document.querySelectorAll('.js-request-status-filter')
    for (const btn of requestStatusBtns) {
        btn.addEventListener('click', () => {
            for (const btn of requestStatusBtns) {
                btn.classList.remove('visit-record_cat-active')
            }
            btn.classList.add('visit-record_cat-active')
            const status = parseBoolean(btn.getAttribute('data-filter'))
            const url = getCurrentUrl()
            const certPage = url.searchParams.get('cert-page')
            const filteredCertificates = getFilteredCertificateData(certificates, status, certPage)
            createRequestBody(filteredCertificates)
            formatDatesInRequestHistory(format_date)
            handle_onclick_certificate_action()
        })
    }
}

function listenRequestDateBtns() {
    const requestDateBtns = document.querySelectorAll('.js-request-date-filter')
    for (const btn of requestDateBtns) {
        btn.addEventListener('click', () => {
            for (const btn of requestDateBtns) {
                btn.classList.remove('js-request-date-active')
            }
            btn.classList.add('js-request-date-active')
            createLogicRequestBarChart()

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

function listenVisitFilters() {
    const visitFilters = document.querySelectorAll('.js-inventory-category')
    for (const visitFilter of visitFilters) {
        visitFilter.addEventListener('click', () => {
            for (const visitFilter of visitFilters) {
                visitFilter.classList.remove('js-inventory-category-active')
                visitFilter.classList.remove('visit-record_cat-active')
            }
            visitFilter.classList.add('js-inventory-category-active')
            visitFilter.classList.add('visit-record_cat-active')
            saveItem('recordVisitFilter', getVisitFilter())
            createLogicVisit()
        })
    }
}

function setSavedParams() {
    if (getItem('recordVisitFilter')) {
        const visitFilters = document.querySelectorAll('.js-inventory-category')
        for (const visitFilter of visitFilters) {
            visitFilter.classList.remove('js-inventory-category-active')
            visitFilter.classList.remove('visit-record_cat-active')
            if (parseInt(visitFilter.getAttribute('data-sorter')) == getItem('recordVisitFilter')) {
                visitFilter.classList.add('js-inventory-category-active')
                visitFilter.classList.add('visit-record_cat-active')
            }
        }
    }
    // Ilagay kung meron visitSearchValue
    if (getItem('recordVisitSearchValue')) {
        document.querySelector('.js-inventory-search-container').value = getItem('recordVisitSearchValue')
    }
    createLogicVisit()
}

function listenVisitSearchBtn() {
    const visitSearchBtn = document.querySelector('.js-inventory-search-btn')
    visitSearchBtn.addEventListener('click', () => {
        //Save search
        saveItem('recordVisitSearchValue', getVisitSearchValue())

        //get search then do logic
        createLogicVisit()

        // Cleanup
        document.querySelector('.js-inventory-search-container').value = ''
        removeItem('recordVisitSearchValue')
    })
}

function listenVisitSearchField() {
    const visitField = document.querySelector('.js-inventory-search-container')
    // Makinig sa kada pindot ni user
    visitField.addEventListener('input', () => {
        // Kunin yung value sa field tapos save locally
        const searchValue = visitField.value
        saveItem('recordVisitSearchValue', searchValue)
    })
}

function createLogicVisit() {
    const filteredHistoryData = filterHistoryData(historyData, getVisitFilter(), getVisitSearchValue())
    const url = getCurrentUrl()
    const page = url.searchParams.get('page')
    const paginatedHistoryData = paginateArray(filteredHistoryData, page)
    createVisitHtml(paginatedHistoryData, formatDate)
    listenViewIllnessesBtn()
    listenViewPatient()
    listenToLinks()
}
