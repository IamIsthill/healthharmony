const patientData = JSON.parse(document.getElementById('patientData').textContent)

main()


function main() {
    setDefault()
    // console.log(patientData)
    updatePatientCount()
    checkPatientPagination()
    formatDatesInPatientsPage(format_date)

    listenToHoverOnPatientName()

    // const item = getPatientDataUsingId(patientData, 23)
    // console.log(item)


}

function setDefault(){
    const patientsPagination = document.querySelector('.js-patients-pagination')
    patientsPagination.style.display = "none"

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
        })
        patient.addEventListener('mouseleave', () => {
            const patientId = patient.getAttribute('data-patient-id')
            const hoverHTML = document.querySelector('.js-hover-patient')
            hoverHTML.remove()

            patient.classList.remove('bordered')
        })
    }
}

function createPatientInformation(data, x, y, format_date) {
    const hoverHTML = document.createElement('div')
    hoverHTML.className = 'js-hover-patient'
    hoverHTML.style.position = 'absolute';
    const date = format_date(data.date_joined)
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

function getPatientDataUsingId(patientData, id) {
    const mid = Math.ceil(patientData.length / 2)
    const firstArr = patientData.slice(0, mid)
    const secondArr = patientData.slice(mid)

    for (const patient of firstArr) {
        if (patient.id == id) {
            return patient
        }
    }

    if (secondArr.length > 0) {
        getPatientDataUsingId(secondArr, id)
    }

    return null
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
