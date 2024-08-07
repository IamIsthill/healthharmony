let illnessData = JSON.parse(document.getElementById('illnessData').textContent)
const illnessModal = document.getElementById('illness_modal')
const modals = document.querySelectorAll('.modal')
const illnessForm = document.getElementById('illness_form')

main()

function createIllnessBody(data){
    let html = ''
    if(data.length <= 0){
        html = `
        <tr>
            <td colspan="4">Congratulations! No pending issue as of this moment.</td>
        </tr>
        `
    } else {
        for(const illness of data){
            if (illness.diagnosis != ''){
                status = 'Released'
            } else {
                status = 'Pending'
            }
            html += `
            <tr>
                <td><span class="patient btn" data-patient-id="${illness.patient_id}">${illness.patient}</span></td>
                <td>${illness.issue}</td>
                <td>${status}</td>
                <td class="view-illness btn" data-issue-id="${illness.id}">View</td>
            </tr>
            `
        }
    }


    document.getElementById('illness_body').innerHTML = html
}

function filterIllnessData(filter){
    let data = illnessData[filter]
    return data
}

async function fetchPredictedDiagnosis(issue){
    try {
        let baseUrl = window.location.origin;
        let url = new URL(`${baseUrl}/doctor/get-diagnosis/`);

        if (issue) {
            url.searchParams.append("issue", issue);
        }
        const options = {
            method: "GET",
        };

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
        } catch (err) {
        console.log(`Failed to fetch session: ${err.message}`);
        return null;
        }
}

async function createIllnessForm(illness) {
    const illnessFormContent = document.getElementById('illness_form_content')
    let diagnosis = await fetchPredictedDiagnosis(illness.issue)
    let html = `

        <h3>Patient Name: ${illness.patient}</h3>
        <label>Illness:</label>
        <textarea type="text" name="issue" required>${illness.issue}</textarea>
        <label>Illness Category:</label>
        <input type="text" name="category" value="${illness.category}" required />
        <input type="hidden" value="${illness.id}" name="id" />
        <label>Diagnosis:</label>
        <textarea type="text" name="diagnosis" value="" required>${diagnosis}</textarea>
        <button type="submit">Update</button>
    `
    illnessFormContent.innerHTML = html
}

function getIllness(id) {
    for (const data of illnessData['all']) {
    if (data.id == id) {
        return data
    }
    }
}

async function main() {
    const closeBtns = document.querySelectorAll('.close')
    for (const btn of closeBtns) {
    btn.addEventListener('click', () => {
        for (const modal of modals) {
        modal.style.display = 'none'
        }
    })
    }

    window.onclick = function (event) {
    if (event.target == illnessModal) {
        for (const modal of modals) {
        modal.style.display = 'none'
        }
    }
    }

    listenIllnessBtns()
    listenPatientBtns()

}

function listenIllnessBtns(){
    const illnessBtns = document.querySelectorAll('.illness-filter')
    illnessBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
        illnessBtns.forEach((btn) => {
            btn.classList.remove('active')
        })
        btn.classList.add('active')
        const text = btn.getAttribute('data-category').toLowerCase()
        const data = filterIllnessData(text)
        createIllnessBody(data)
        listenViewIllnessBtns()
        listenPatientBtns()
        })
    })
}

function listenViewIllnessBtns(){
    const viewIllnessBtns = document.querySelectorAll('.view-illness')
    for (const btn of viewIllnessBtns) {
        btn.addEventListener('click', () => {
        const illnessId = parseInt(btn.getAttribute('data-issue-id'))
        console.log(illnessId)
        const illness = getIllness(illnessId)
        createIllnessForm(illness)
        illnessModal.style.display = 'block'
        })
    }
}

function listenPatientBtns(){
    const patientBtns = document.querySelectorAll('.patient')
    for(const btn of patientBtns){
        btn.addEventListener('click', ()=>{
            const patientId = parseInt(btn.getAttribute('data-patient-id'))
            let baseUrl = window.location.origin;
            let url = new URL(`${baseUrl}/doctor/patient/${patientId}/`);
            window.location.href = url
        })
    }
}
