export function get_filtered_illnesses_data(illnessesData, filter) {
    let data = []

    if (filter == 'all') {
        data = illnessesData
    } else {
        for (const illness of illnessesData) {
            if (filter == 'not') {
                if (!illness.diagnosis) {
                    data.push(illness)
                }
            } else if (filter == 'done') {
                if (illness.diagnosis) {
                    data.push(illness)
                }
            }
        }
    }

    return data
}

export function get_expand_btn() {
    const btn = document.createElement('button')
    btn.classList.add('js-expand-illness-btn')
    btn.innerText = 'Expand'

    return btn
}

export function get_leave_notes_btn(id) {
    const btn = document.createElement('button')
    btn.setAttribute('illness-id', id)
    btn.innerHTML = `
        <span class="material-symbols-outlined">edit_note</span>Send a Note
    `
    btn.classList.add('js-illness-note-btn')
    return btn
}

export function get_edit_btn() {
    const btn = document.createElement('button')
    btn.classList.add('js-edit-illness-btn')
    btn.innerText = 'Edit'

    return btn
}

export function get_treatment_data_using_id(id, treatmentData) {
    for (const treatment of treatmentData) {
        if (parseInt(treatment.inventory_detail) == parseInt(id)) {
            return treatment
        }
    }
    return null
}

export function get_illness_data(id, illnessesData) {
    for (const illness of illnessesData) {
        if (parseInt(illness.id) == parseInt(id)) {
            return illness
        }
    }
    return null
}
