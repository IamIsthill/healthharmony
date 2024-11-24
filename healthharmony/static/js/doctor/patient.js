import {
    formatDate,
    openModal,
    closeModal,
    getToken
} from '../utils.js'

import {
    get_filtered_illnesses_data,
    get_expand_btn,
    get_edit_btn,
    get_leave_notes_btn,
    get_treatment_data_using_id,
    get_illness_data,
} from './patient-history.js'

import {
    get_category_element,
    get_csrf_element,
    get_diagnosis_element,
    get_issue_element,
    get_medicine_element,
    get_quantity_element,
    get_treatments_element,
    get_illnesss_id_element
} from './patient-form.js'

const userId = JSON.parse(document.getElementById('userId').textContent)
const userAccess = JSON.parse(document.getElementById('userAccess').textContent)
const illnessesData = JSON.parse(document.getElementById('illnessData').textContent)
const treatmentData = JSON.parse(document.getElementById('treatmentData').textContent)
const patient_data = JSON.parse(document.getElementById('patient_data').textContent)
const department_data = JSON.parse(document.getElementById('department_data').textContent)
const illness_notes_data = JSON.parse(document.getElementById('illness_notes_data').textContent)
const illness_categories = await fetch_illness_categories()
const inventory_list = await fetch_inventory_list()


main()

async function main() {
    /** MAKE HTML PRESENTABLE AND DATA PREPATION*/
    update_existing_dates_to_readable()
    append_category_list(illness_categories)

    /** Visit History */
    filter_visit_history()
    click_expand_show_treatments()
    click_edit_show_form()

    //Notes related
    handle_onclick_send_notes()
    attach_btn_if_illness_has_notes()
    handle_onclick_view_notes()

    /** Detailed info */
    handle_onclick_edit_patient()

    /** Vital Info */
    handle_onclick_edit_vital()

}

// Add event listener to the view notes
function handle_onclick_view_notes() {
    const btns = document.querySelectorAll('.js_view_notes')

    if (btns.length == 0) {
        return
    }

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            // Get the illness id in the html
            const illness_id = parseInt(btn.getAttribute('illness-id'))

            const notes_div = document.querySelector('.js_notes_body')
            notes_div.innerHTML = ''

            for (const notes of Object.values(illness_notes_data)) {
                if (parseInt(notes.attached_to) == illness_id) {
                    const sender = notes.doctor_first_name != '' && notes.doctor_first_name && notes
                        .doctor_last_name != '' && notes.doctor_last_name ?
                        `${notes.doctor_first_name} ${notes.doctor_last_name}` : `${notes.doctor_email}`
                    notes_div.innerHTML += `
                        <div class = "view-notes-cont"> 
                            <div class = "msg-div">
                            <h5>Message</h5>
                            <p> ${notes.notes} 
                            </div>

                            <p>Sent by: ${sender}</p>
                            <p>Date: ${formatDate(notes.timestamp)}</p>
                        </div>
                    `

                }
            }
            notes_div.innerHTML += `
              <button class="js-illness-note-btn view-send-btn" illness-id="${illness_id}"><span class="material-symbols-outlined">edit_note</span>Send a Note</button>

            `

            let modal = document.querySelector('.js_view_notes_modal')
            const close_btns = document.querySelectorAll('.js-close-btn')

            openModal(modal)

            for (const close of close_btns) {
                closeModal(modal, close)
            }


            const send_notes_btns = document.querySelectorAll('.js-illness-note-btn')

            for (const send_notes_btn of send_notes_btns) {
                send_notes_btn.addEventListener('click', () => {
                    modal = document.querySelector('.js_view_notes_modal')
                    modal.style.display = 'none'
                })
            }



            handle_onclick_send_notes()



        })

    }




}

// Attach view notes button in illnesses
function attach_btn_if_illness_has_notes() {
    if (illness_notes_data.length == 0) {
        return;
    }

    const illness_cases = document.querySelectorAll('.js-illness');

    if (illness_cases.length == 0) {
        return;
    }

    for (const illness_case of illness_cases) {
        const illness_id = parseInt(illness_case.getAttribute('data-illness-id'));

        // Check if the illness has notes related to it
        for (const notes of Object.values(illness_notes_data)) {
            if (parseInt(notes.attached_to) == illness_id) {
                const btn = document.createElement('button');
                btn.setAttribute('illness-id', illness_id);
                btn.classList.add('js_view_notes');
                btn.classList.add('view-btn');

                // Create the icon element
                const icon = document.createElement('span');
                icon.classList.add('material-symbols-outlined');
                icon.innerText = 'visibility';

                // Add the icon and the button text
                btn.appendChild(icon);
                btn.appendChild(document.createTextNode(' View Notes'));

                // Add the button to the illness case
                illness_case.appendChild(btn);
                break;
            }
        }
    }
}


// Handle when user clicks send notes
function handle_onclick_send_notes() {
    const btns = document.querySelectorAll('.js-illness-note-btn')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            const illness_id = btn.getAttribute('illness-id')
            const illness_data = get_illness_data(illness_id, illnessesData)

            const form = document.querySelector('.js_send_notes_form')
            form.innerHTML = ''

            form.innerHTML = `
                <div>
                    <h2>Case Details</h2>
                    <div class = "case-row">
                        <h3>Symptoms:</h3> <span> ${illness_data.issue}</span>
                    </div>
                    <div class = "case-row">
                        <h3>Symptom Category:</h3> <span>${illness_data.category_name ? illness_data.category_name: ''}</span>
                    </div>
                    <div class = "case-row">
                        <h3>Diagnosis:</h3> <span> ${illness_data.diagnosis ? illness_data.diagnosis : ''}</span>
                    </div>
                </div>
            `

            //Attach the hidden csrf element
            form.appendChild(get_csrf_element(getToken()))

            const illness_id_element = document.createElement('input')
            illness_id_element.setAttribute('type', 'hidden')
            illness_id_element.setAttribute('name', 'illness_id')
            illness_id_element.setAttribute('required', '')
            illness_id_element.value = illness_id

            form.appendChild(illness_id_element)

            const label_element = document.createElement('label')
            label_element.innerText = 'Message: '

            form.appendChild(label_element)

            const textarea_element = document.createElement('textarea')
            textarea_element.setAttribute('name', 'message')

            form.appendChild(textarea_element)

            form.innerHTML += `
            <div class = "form-buttons">
                <button type='button' class="js-close-btn cancel-button">Cancel</button>
                <button class = "form-button" type='submit'>Send</button>
            </div>
            `

            const modal = document.querySelector('.js_send_notes_modal')
            const close_btns = document.querySelectorAll('.js-close-btn')

            openModal(modal)

            for (const close of close_btns) {
                closeModal(modal, close)

            }


        })
    }
}


function click_edit_show_form() {
    const edit_btns = document.querySelectorAll('.js-edit-illness-btn')

    if (edit_btns.length > 0) {
        for (const btn of edit_btns) {
            btn.addEventListener('click', () => {
                const illness_id = btn.parentElement.getAttribute('data-illness-id')
                const illness_data = get_illness_data(illness_id, illnessesData)

                create_illness_edit_form(illness_data, illness_categories)

                const modal = document.querySelector('.js-edit-illness-modal')
                const close_btns = document.querySelectorAll('.js-close-btn')
                openModal(modal)
                for (const close of close_btns) {
                    closeModal(modal, close)
                }
            })
        }
    }
}

function add_more_prescription(inventory_list) {
    const add_more_btn = document.querySelector('.js_add_more_btn')

    if (!add_more_btn) {
        return
    }

    add_more_btn.addEventListener('click', (event) => {
        event.preventDefault()
        const inventory_item_elements = document.querySelectorAll('select[name="inventory_item"]')
        const inventory_quantity_elements = document.querySelectorAll('input[name="inventory_quantity"]')

        if (
            is_element_valid(inventory_item_elements) &&
            is_element_valid(inventory_quantity_elements)
        ) {
            const container = document.createElement('div')
            const medicine_element = get_medicine_element(inventory_list)
            const quantity_element = get_quantity_element()

            container.append(medicine_element, quantity_element)
            const add_more_btn = document.querySelector('.js_add_more_btn')
            add_more_btn.insertAdjacentElement('beforebegin', container)

            return
        }
    })
}

function is_element_valid(elements) {
    for (const element of elements) {
        if (!element.reportValidity()) {
            return false
        }
    }
    return true
}

function update_existing_dates_to_readable() {
    const dates = document.querySelectorAll('.js-dates')

    for (const date of dates) {
        date.innerText = formatDate(date.innerText)
    }
}

function filter_visit_history() {
    const filterBtns = document.querySelectorAll('.js-illness-filter')

    for (const btn of filterBtns) {
        btn.addEventListener('click', () => {
            const filter = btn.getAttribute('data-category')

            //CSS
            for (const btn of filterBtns) {
                btn.classList.remove('visit_cat-active')
            }
            btn.classList.add('visit_cat-active')

            const filtered_illness_data = get_filtered_illnesses_data(illnessesData, filter)

            update_visit_html_after_filter(filtered_illness_data)
            click_expand_show_treatments()
            handle_onclick_send_notes()

        })
    }
}

async function create_illness_edit_form(illness_data, illness_categories) {
    const form_body = document.querySelector('.js-edit-illness-modal form')
    form_body.innerHTML = ''
    const token = getToken()
    form_body.append(get_csrf_element(token), get_illnesss_id_element(illness_data.id))
    form_body.innerHTML += '<label>Symptoms: </label>'
    form_body.appendChild(get_issue_element(illness_data.issue))
    form_body.innerHTML += '<label>Category of Symptoms: </label>'
    form_body.appendChild(get_category_element(illness_data.category_name, illness_categories))

    form_body.innerHTML += '<label>Diagnosis: </label>'
    const diagnosis = await fetchPredictedDiagnosis(illness_data.issue)

    if ((illness_data.diagnosis == '' || !illness_data.diagnosis) && diagnosis) {
        form_body.appendChild(get_diagnosis_element(diagnosis))
        form_body.innerHTML += `
            <p class="illness-error-message">This is system generated and may be inaccurate. Please ensure that they are correct.</p>
        `
    } else {
        form_body.appendChild(get_diagnosis_element(illness_data.diagnosis))
    }
    const treatment_element = get_treatments_element(illness_data, inventory_list, treatmentData)
    if (illness_data.treatment.length == 0) {
        form_body.appendChild(treatment_element)
    }
    form_body.innerHTML += '<button type="submit" class="js_illness_edit_btn update-case">Update Case</button>'

    add_more_prescription(inventory_list)

    const diagnosis_field = document.querySelector('.js_illness_diagnosis_field')
    diagnosis_field.addEventListener('input', () => {
        const message = document.querySelector('.illness-error-message')
        if(message)(
            message.remove()
        )
    })
    // send_updated_illness_case()
}

function append_category_list(illness_categories) {
    const form_body = document.querySelector('.js-edit-illness-modal form')
    const element = document.createElement('datalist')
    element.setAttribute('id', 'js_categories_list')
    let html = ''
    for (const category of illness_categories) {
        html += `<option value="${category.category}">`
    }
    element.innerHTML = html
    form_body.insertAdjacentElement('afterend', element)
}

function click_expand_show_treatments() {
    const expand_btns = document.querySelectorAll('.js-expand-illness-btn')

    if (expand_btns.length > 0) {
        for (const btn of expand_btns) {
            btn.addEventListener('click', () => {
                if (btn.innerText == 'Expand') {
                    btn.previousElementSibling.classList.remove('hide')
                    btn.innerText = 'Close'
                } else if (btn.innerText == 'Close') {
                    btn.previousElementSibling.classList.add('hide')
                    btn.innerText = 'Expand'
                }
            })

        }
    }
}

function update_visit_html_after_filter(filtered_illness_data) {
    const illness_history_html = document.querySelector('.illness_body')
    illness_history_html.innerHTML = ''
    if (filtered_illness_data.length == 0) {
        illness_history_html.innerHTML = '<h4>No visit history on this category</h4>'
    } else {
        for (const illness of filtered_illness_data) {
            const illness_div = document.createElement('div')
            illness_div.setAttribute('data-illness-id', illness.id)
            illness_div.classList.add('js-illness')

            if (parseInt(userAccess) >= 3) {
                const edit_btn = get_edit_btn()
                illness_div.appendChild(edit_btn)
            }

            const info_cont = document.createElement('div')
            info_cont.classList.add('info-cont')

            const visit_left = document.createElement('div')
            visit_left.classList.add('visit-left')
            visit_left.innerHTML = `
                <span>Date and Time:</span>
                <span>Symptoms:</span>
                <span>Category of Symptom:</span>
                <span>Diagnosis:</span>
            `

            const visit_right = document.createElement('div')
            visit_right.classList.add('visit-right')
            visit_right.innerHTML = `
            <p>${formatDate(illness.added)}</p>
            <p>${illness.issue}</p>
            <p>${illness.category_name ? illness.category_name : ''}</p>
            <p> ${illness.diagnosis ? illness.diagnosis : ''}</p>
            `
            info_cont.appendChild(visit_left)
            info_cont.appendChild(visit_right)

            illness_div.appendChild(info_cont)

            if (illness.treatment.length > 0) {
                const treatment_div = create_treatment_list(illness.treatment, treatmentData)
                illness_div.appendChild(treatment_div)

                const expand_btn = get_expand_btn()
                illness_div.appendChild(expand_btn)
            }

            const note_btn = get_leave_notes_btn(illness.id)
            illness_div.appendChild(note_btn)

            illness_history_html.appendChild(illness_div)
        }
        click_edit_show_form()

    }
}

function create_treatment_list(treatments, treatmentData) {
    const treatment_div = document.createElement('div')
    treatment_div.classList.add('js-treatment-list')
    treatment_div.classList.add('hide')
    treatment_div.innerHTML = '<p>Treatments:</p>'
    let treatment_list_html = ''
    for (const id of treatments) {
        const treatment = get_treatment_data_using_id(id, treatmentData)
        treatment_list_html +=
            `<li>${treatment.inventory_detail_category}: ${treatment.inventory_detail_name} ${treatment.quantity} ${treatment.inventory_detail_unit}</li>`
    }
    treatment_div.innerHTML += treatment_list_html
    return treatment_div
}

async function fetchPredictedDiagnosis(issue) {
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
        console.error(`Failed to fetch session: ${err.message}`);
        return null;
    }
}

async function fetch_illness_categories() {
    try {
        const baseUrl = window.location.origin
        const url = new URL(`${baseUrl}/doctor/get_illness_categories`)
        const options = {
            method: "GET"
        }
        const response = await fetch(url, options)
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();

    } catch (error) {
        console.error(`Failed to get illness categories: ${error.message}`)
        return null
    }
}

async function fetch_inventory_list() {
    try {
        const baseUrl = window.location.origin
        const url = new URL(`${baseUrl}/doctor/get_inventory_list/`)
        const options = {
            method: "GET"
        }
        const response = await fetch(url, options)
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();

    } catch (error) {
        console.error(`Failed to get illness categories: ${error.message}`)
        return null
    }
}

// when user click the edit patient info btn, create the form
function handle_onclick_edit_patient() {
    const btn = document.querySelector('.js_edit_patient_btn')

    btn.addEventListener('click', () => {
        btn.setAttribute('style', 'display: none')
        const labels_element = document.querySelector('.js_patient_labels')

        // Save the content of labels
        const old_labels = labels_element.innerHTML

        const department_list_element = document.createElement('datalist')
        department_list_element.setAttribute('id', 'department_list')
        for (const department of department_data) {
            department_list_element.innerHTML += `
                <option value="${department.department}">${department.department}</option>
            `
        }

        labels_element.innerHTML = `
            <form action="/doctor/patient/post_update_user_details/" method="POST">
                    <input name="csrfmiddlewaretoken" value="${getToken()}" type="hidden" />
                    <input name="patient_id" value="${patient_data.id}" type="hidden" />
            <div class="visit-row">
                <span class="js_form_age_label">Date of Birth:</span>
                 <input name="DOB" value="${patient_data.DOB ? patient_data.DOB : ''}" type="date" required />
              </div>
              <div class="visit-row">
                <span>Sex</span>
                <select name="sex">
                    <option value="Male" ${patient_data.sex=='Male' ? 'selected': ''}>Male</option>
                    <option value="Female" ${patient_data.sex=='Female' ? 'selected': ''}>Female</option>
                </select>
              </div>
              <div class="visit-row">
                <span>Contact</span>
                <input name="contact" value="${patient_data.contact ? patient_data.contact : ''}" type="text" placeholder="contact" required />
              </div>
              <div class="visit-row">
                <span>Year</span>
                <select name="year" class = "year-select">
            <option value="1" ${patient_data.year==1 ? 'selected' : ''}>1</option>
            <option value="2" ${patient_data.year==2 ? 'selected' : ''}>2</option>
            <option value="3" ${patient_data.year==3 ? 'selected' : ''}>3</option>
            <option value="4" ${patient_data.year==4 ? 'selected' : ''}>4</option>
            <option value="5" ${patient_data.year==5 ? 'selected' : ''}>5</option>
        </select>
              </div>
              <div class="visit-row">
                <span>Section</span>
                 <input name="section" value="${patient_data.section ? patient_data.section : ''}" type="text" placeholder="section" required />
              </div>
              <div class="visit-row">
                <span>Program</span>
                <input name="program" value="${patient_data.program ? patient_data.program : ''}" type="text" placeholder="Program..." required/>
              </div>
              <div class="visit-row">
                <span>Department</span>
                 <input name="department" value="${patient_data.department_name ? patient_data.department_name : ''}" type="text" placeholder="Department..." list="department_list" required />
              </div>
              <div class = "edit-buttons">
            <button class ="update-btn" type="submit">Update</button>
            <button type="button" class="js_cancel_pattient_btn cancel-btn">Cancel</button>
        </div>

            </form>
        `

        // Add the department list in the form
        labels_element.appendChild(department_list_element)


        const cancel_btn = document.querySelector('.js_cancel_pattient_btn')

        cancel_btn.addEventListener('click', () => {
            labels_element.innerHTML = old_labels
            btn.setAttribute('style', '')
        })
        filter_inputs_number_field()
    })
}

// get the form for updating patient detailss
function get_form_element_for_patient_details() {
    // creaet the form
    const form_element = document.createElement('form')
    form_element.setAttribute('method', 'POST')
    form_element.setAttribute('action', '/doctor/patient/post_update_user_details/')
    form_element.classList.add('detailed-right')

    const department_list_element = document.createElement('datalist')
    department_list_element.setAttribute('id', 'department_list')

    for (const department of department_data) {
        department_list_element.innerHTML += `
            <option value="${department.department}">${department.department}</option>
        `
    }

    form_element.innerHTML = `

        <input name="csrfmiddlewaretoken" value="${getToken()}" type="hidden" />
        <input name="patient_id" value="${patient_data.id}" type="hidden" />
        <input name="DOB" value="${patient_data.DOB ? patient_data.DOB : ''}" type="date" required />
        <input name="sex" value="${patient_data.sex ? patient_data.sex: ''}" type="text" required />
        <input name="contact" value="${patient_data.contact ? patient_data.contact : ''}" type="text" placeholder="contact" required />
        <div class = "year-section">
        <select name="year">
            <option value="1" ${patient_data.year==1 ? 'selected' : ''}>1</option>
            <option value="2" ${patient_data.year==2 ? 'selected' : ''}>2</option>
            <option value="3" ${patient_data.year==3 ? 'selected' : ''}>3</option>
            <option value="4" ${patient_data.year==4 ? 'selected' : ''}>4</option>
            <option value="5" ${patient_data.year==5 ? 'selected' : ''}>5</option>
        </select>
        <input name="section" value="${patient_data.section ? patient_data.section : ''}" type="text" placeholder="section" required />
        </div>
        <input name="program" value="${patient_data.program ? patient_data.program : ''}" type="text" placeholder="Program..." required/>
        <input name="department" value="${patient_data.department_name ? patient_data.department_name : ''}" type="text" placeholder="Department..." list="department_list" required />

    `
    form_element.appendChild(department_list_element)
    form_element.innerHTML += `
        <div class = "edit-buttons">
            <button class ="update-btn" type="submit">Update</button>
            <button type="button" class="js_cancel_pattient_btn cancel-btn">Cancel</button>
        </div>
    `

    return form_element
}

// user clicks the edit button for the vital statistics
function handle_onclick_edit_vital() {
    const btn = document.querySelector('.js_edit_vital_btn')

    btn.addEventListener('click', () => {
        const vital_labels = document.querySelector('.js_patient_vital_labels')
        btn.setAttribute('style', 'display:none')


        const info_vitals_element = vital_labels.nextElementSibling

        vital_labels.nextElementSibling.remove()

        const form_element = get_form_element_for_patient_vital()

        vital_labels.insertAdjacentElement('afterend', form_element)

        const cancel_btn = document.querySelector('.js_cancel_pattient_btn')

        cancel_btn.addEventListener('click', () => {
            vital_labels.nextElementSibling.remove()
            vital_labels.insertAdjacentElement('afterend', info_vitals_element)
            btn.setAttribute('style', '')
        })

        filter_inputs_number_field()

    })
}

// Create the form for editing vital patietn info
function get_form_element_for_patient_vital() {
    const form_element = document.createElement('form')
    form_element.setAttribute('method', "POST")
    form_element.setAttribute('action', "/doctor/patient/post_update_user_vitals/")
    form_element.classList.add('vital-right')

    form_element.innerHTML = `

        <input name="csrfmiddlewaretoken" value="${getToken()}" type="hidden" />
        <input name="patient_id" value="${patient_data.id}" type="hidden" />
        <input class = "blood-input" name="blood_type" value="${patient_data.blood_type ? patient_data.blood_type : '' }" type="text" placeholder="Patient's blood type..." list="blood_list"/>
        <datalist id="blood_list">
            <option value="A+">
            <option value="A-">
            <option value="B+">
            <option value="B-">
            <option value="AB+">
            <option value="AB-">
            <option value="O+">
            <option value="O-">
        </datalist>
        <input name="height" value="${patient_data.height ? patient_data.height : ''}" type="number" required placeholder="Patient's height..." pattern="[0-2]$" />
        <input name="weight" value="${patient_data.weight ? patient_data.weight : ''}" type="number" required placeholder="Patient's weight..." />
        <div class = "edit-buttons">
            <button class ="update-btn" type="submit">Update</button>
            <button type="button" class="js_cancel_pattient_btn cancel-btn">Cancel</button>
        </div>

    `

    return form_element


}

function filter_inputs_number_field() {
    const input_elements = document.querySelectorAll('input[type="number"]')

    if (input_elements.length == 0) {
        return
    }

    for (const input_element of input_elements) {
        input_element.addEventListener('keydown', (event) => {
            if (event.key == 'e' || event.key == 'E') {
                event.preventDefault()
            }
        })

        input_element.addEventListener('input', () => {
            const input = input_element.value
            const number_pattern = /([1-9][.][0-9])|([1-9])/
            const number_pattern2 = /^[0-9]*\.?[0-9]*$/
            const test = number_pattern2.test(input)
            if (!test) {
                input_element.value = input.slice(0, input.length - 1)
            }
        })

        input_element.addEventListener('input', () => {
            let number = input_element.value
            if (number.length > 11) {
                number = number.slice(0, 11)
            }
            input_element.value = number
        })


    }
}
