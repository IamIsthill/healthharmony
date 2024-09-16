import {
    openModal,
    closeModal,
    formatDate
  } from '/static/js/utils.js'

const illness_data = JSON.parse(document.getElementById('illness_data').textContent)
const treatment_data = JSON.parse(document.getElementById('treatment_data').textContent)
const illness_category = JSON.parse(document.getElementById('illness_category').textContent)
const certificate_data = JSON.parse(document.getElementById('certificate_data').textContent)
console.log(certificate_data)
/**MEDCERT */
handle_onclick_request_medcert()

/** OVERALL */
update_dates(formatDate)

/** VISIT HISTROY */
handle_onclick_show_more_illness()



// User clicks the button for requesting a medical certificate
function handle_onclick_request_medcert() {
    const btn = document.querySelector('.js_request_medcert_btn')

    btn.addEventListener('click', () => {
      const modal = document.querySelector('.js_request_medcert_modal')
      const close_btns = document.querySelectorAll('.js_close_medcert_modal')

      openModal(modal)

      for (const close of close_btns) {
        closeModal(modal, close)
      }

    })
}

// User clicks show more btn
function handle_onclick_show_more_illness() {
    const btns = document.querySelectorAll('.js_show_illness_details')

    if (btns.length == 0) {
        return
    }

    for (const btn of btns) {
        btn.addEventListener('click', () => {

            const illness_id = btn.getAttribute('data-illness-id')
            const illness = get_illness_data(illness_id, illness_data)

            const treatments_element = document.createElement('div')

            for (const id of illness.treatment) {
                const treatment = get_treatment_data(id, treatment_data)
                treatments_element.innerHTML += `
                <p>${treatment.inventory_detail_name} - ${treatment.quantity * -1} ${treatment.inventory_detail_unit ? treatment.inventory_detail_unit : '' }</p>
                `
            }



            const illness_space_element = btn.previousElementSibling
            illness_space_element.innerHTML = `
                <h4>Diagnosis : ${illness.diagnosis}
                <h5> Treatments: </h5>
            `
            illness_space_element.appendChild(treatments_element)


            if (btn.classList.contains('js_active')) {
                btn.innerText = 'Show More'
                btn.classList.remove('js_active')
                illness_space_element.classList.add('hide')
            }
            else {
                btn.innerText = 'Close'
                btn.classList.add('js_active')
                illness_space_element.classList.remove('hide')
            }


        })
    }
}
  // Make dates more readable
function update_dates(formatDate) {
    const dates = document.querySelectorAll('.js_dates')

    for (const date of dates) {
        date.textContent = formatDate(date.textContent)
    }
}

// Get illness details for the case
function get_illness_data(illness_id, illness_data) {
    for (const illness of illness_data) {
        if (parseInt(illness.id) == parseInt(illness_id)) {
            return illness
        }
    }
    return null
}

// Get the treatment details for illness
function get_treatment_data(inventory_detail, treatment_data) {
    for (const inventory of treatment_data) {
        if(parseInt(inventory.inventory_detail) == parseInt(inventory_detail)) {
            return inventory
        }
    }
    return null
}
