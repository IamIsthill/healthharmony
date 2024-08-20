import {
    openModal,
    closeModal,
} from '/static/js/utils.js'

import {
    createViewIllnessBody,
    format_date,
    getIllnessUsingId
} from '/static/js/staff/record-visit.js'


const historyData = JSON.parse(document.getElementById('history-data').textContent)
main()

function main() {
    // console.log(historyData)
    listenAddRecordBtn()
    formatDatesInVisitHistory()
    listenViewIllnessesBtn()
}

function listenViewIllnessesBtn() {
    const viewIllnessBtns = document.querySelectorAll('.js-view-illness-btn')
    for (const viewIllnessBtn of viewIllnessBtns) {
        viewIllnessBtn.addEventListener('click', () => {
            const illnessId = parseInt(viewIllnessBtn.getAttribute('data-illness-id'))
            const illnessData = getIllnessUsingId(historyData, illnessId)
            console.log(illnessData.treatment)
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


function formatDatesInVisitHistory() {
    const dateStrings = document.querySelectorAll('.date')
    for (const date of dateStrings) {
        const newDate = format_date(date.textContent)
        date.innerText = newDate
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
