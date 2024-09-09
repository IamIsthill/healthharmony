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

export function get_leave_notes_btn() {
    const btn = document.createElement('button')
    btn.classList.add('js-leave-note-btn')
    btn.innerText = 'Leave Notes'
    return btn
}

export function get_edit_btn() {
    const btn = document.createElement('button')
    btn.classList.add('js-edit-illness-btn')
    btn.innerText = 'Edit'

    return btn
}
