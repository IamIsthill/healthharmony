import {
    getCurrentUrl
} from '/static/js/utils.js'

import {
    getPatientDataUsingId,
    createPatientInformation,
    checkIfFilterExist,
    getFilterParams,
    filterPatientData,
    getPatientFilter
} from '/static/js/staff/account-patients.js'

const patientData = JSON.parse(document.getElementById('patientData').textContent)

main()


function main() {
    setDefault()
    // for (const patient of patientData) {
    //     console.log(patient.profile)
    // }
    updatePatientCount()
    checkPatientPagination()
    formatDatesInPatientsPage(format_date)
    listenToHoverOnPatientName()

    listenPatientFilter()
    listenPatientSearchBtn()

    const patientPage = getCurrentUrl().searchParams.get('patients-page')
    const filterParams = getFilterParams(getPatientFilter())
    const filteredPatientData = filterPatientData(filterParams, patientData, '')
    // paginatePatientData(filteredPatientData, patientPage)





}

function setDefault(){
    const patientsPagination = document.querySelector('.js-patients-pagination')
    patientsPagination.style.display = "none"

}

function listenPatientSearchBtn() {
    const patientSearchBtn = document.querySelector('.js-patient-search-btn')
    patientSearchBtn.addEventListener('click', () => {
        const patientSearchField = document.querySelector('.js-patient-search-field')
        const searchText = patientSearchField.value
        const filterParams = getFilterParams(getPatientFilter())
        const filteredPatientData = filterPatientData(filterParams, patientData, searchText)
    })
}

function paginatePatientData(filteredPatientData, patientPage) {
    if(!patientPage) {
        patientPage = 1
    }

    patientPage = parseInt(patientPage)
    let itemStart = patientPage * 10 - 9
    let itemEnd = patientPage * 10
    if (itemStart > filteredPatientData.length) {
        patientPage = Math.ceil(filteredPatientData.length / 10)

    }
    if (Math.ceil(filteredPatientData.length / 10) < patientPage) {
        itemStart = patientPage * 10 - 9
        itemEnd = patientPage * 10
    }

    for (let key in filteredPatientData) {
        key = parseInt(key)
        if ( key + 1  >= itemStart && key + 1 <= itemEnd ) {
            console.log(filteredPatientData[key])
        }
        // console.log(itemStart, key+1, itemEnd)
    }

}





function listenPatientFilter() {
    const patientFilterInput = document.querySelector('.js-patient-filter-inputs')
    patientFilterInput.addEventListener('change', () => {
        const filter = patientFilterInput.value
        if(filter) {
            if (!checkIfFilterExist(filter)) {
                updatePatientFilters(filter)
            }
        }
        clickToRemovePatientFilter()

        getPatientFilter()
    })
}





function clickToRemovePatientFilter() {
    const filterInstances = document.querySelectorAll('.js-patient-filter')
    for (const filterInstance of filterInstances) {
        filterInstance.addEventListener('click', () => {
            filterInstance.remove()
        })
    }
}

function updatePatientFilters(filter) {
    const patientFilters = document.querySelector('.js-patient-filters')
    let filterCollectionHTML = patientFilters.innerHTML
    const filterHTML = `
        <div class="js-patient-filter" data="${filter}">
            <p>${filter.toUpperCase()}  <span class="js-close-button">x</span></p>

        </div>
    `
    filterCollectionHTML += filterHTML
    patientFilters.innerHTML = filterCollectionHTML
}

function listenToHoverOnPatientName() {
    const patients = document.querySelectorAll('.js-patient-profile')
    for (const patient of patients) {
        patient.addEventListener('mouseenter', (event) => {
            const patientId = parseInt(patient.getAttribute('data-patient-id'))
            const data = getPatientDataUsingId(patientData, patientId)
            const x = event.clientX, y = event.clientY
            createPatientInformation(data, x, y, format_date)
            patient.classList.add('bordered')

            patient.addEventListener('mouseleave', () => {
                const hoverHTML = document.querySelectorAll('.js-hover-patient')
                for (const html of hoverHTML){
                    html.remove()
                }
                patient.classList.remove('bordered')
            })
        })
    }
}

function formatDatesInPatientsPage(format_date) {
    const dates = document.querySelectorAll('.js-dates')
    for (const date of dates) {
        try {
            const formattedDate = format_date(date.innerText)
            if (formattedDate.includes('Invalid Date')) {
                date.innerText = ' '
                continue
            }
            date.innerText = formattedDate
        } catch(error) {
            console.error(error)
        }
    }
}

function format_date(dateString) {
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

function checkPatientPagination() {
    try {
        const patientsPagination = document.querySelector('.js-patients-pagination')
        const count = patientData.length
        if (count > 1) {
            patientsPagination.style.display = "block"
        }
    } catch(error) {
        console.log(error)
    }
}

function updatePatientCount() {
    const patientCountElement = document.querySelector('.js-patient-count')
    const count = patientData.length
    let content = null
    if (count > 1) {
        content = `All Patients(${count})`
    } else {
        content =  `All Patient(${count})`
    }
    patientCountElement.innerText = content
}
