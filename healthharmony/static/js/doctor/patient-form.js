import {
    get_treatment_data_using_id
} from './patient-history.js'

export function get_add_more_btn() {
    const add_more_btn = document.createElement('button');
    add_more_btn.classList.add('js_add_more_btn');
    add_more_btn.innerText = 'Add More';

    return add_more_btn;
}

export function get_medicine_element(inventory_list) {
    const medicine_element = document.createElement('select')
    medicine_element.setAttribute('required', '')
    medicine_element.setAttribute('name', 'inventory_item')

    if (inventory_list.length == 0) {
        return ''
    }

    for (const option of inventory_list) {
        medicine_element.innerHTML += `<option value="${option.item_name}">${option.item_name}</option>`
    }

    return medicine_element
}

export function get_quantity_element() {
    const quantity_element = document.createElement('input')
    quantity_element.setAttribute('required', '')
    quantity_element.setAttribute('type', 'number')
    quantity_element.setAttribute('name', 'inventory_quantity')
    quantity_element.setAttribute('placeholder', 'Item quantity...')

    return quantity_element
}
export function get_csrf_element(token) {
    const element = document.createElement('input')
    element.setAttribute('name', 'csrfmiddlewaretoken')
    element.value = token
    element.setAttribute('required', '')
    element.setAttribute('type', 'hidden')
    return element
}
export function get_diagnosis_element(diagnosis) {
    const element = document.createElement('textarea')
    element.setAttribute('name', 'diagnosis')
    element.setAttribute('value', diagnosis)
    element.setAttribute('required', '')
    element.setAttribute('type', 'text')
    element.innerText = diagnosis
    return element
}
export function get_category_element(category) {
    category = category ? category : ''
    const element = document.createElement('input')
    element.setAttribute('name', 'category')
    element.setAttribute('value', category)
    element.setAttribute('required', '')
    element.setAttribute('type', 'text')
    element.setAttribute('list', 'js_categories_list')
    return element
}
export function get_issue_element(issue) {
    const element = document.createElement('input')
    element.setAttribute('name', 'issue')
    element.setAttribute('value', issue)
    element.setAttribute('required', '')
    element.setAttribute('type', 'text')
    return element
}

export function get_illnesss_id_element(id) {
    const element = document.createElement('input')
    element.setAttribute('name', 'illness_id')
    element.setAttribute('value', id)
    element.setAttribute('required', '')
    element.setAttribute('type', 'hidden')
    return element

}
export function get_treatments_element(treatments, inventory_list, treatmentData) {
    const treatment_div_element = document.createElement('div')
    if (inventory_list.length > 0) {
        treatment_div_element.classList.add('js_treatment_fields')
        treatment_div_element.innerHTML += `<label>Prescriptions: </label>`

    }
    // treatment_div_element.classList.add('js_treatment_fields')
    // treatment_div_element.innerHTML += `<label>Prescriptions: </label>`
    const quantity_element = get_quantity_element()

    if (treatments.length == 0) {
        const container = document.createElement('div')
        const medicine_element = get_medicine_element(inventory_list)

        if (medicine_element != '') {
            container.append(medicine_element, quantity_element)
        }
        treatment_div_element.appendChild(container)

    } else {
        for (const id of treatments) {
            const container = document.createElement('div')

            const medicine_element = get_medicine_element(inventory_list)
            medicine_element.setAttribute('value', (get_treatment_data_using_id(id, treatmentData))
                .inventory_detail_name)

            if (medicine_element != '') {
                quantity_element.setAttribute('value', (get_treatment_data_using_id(id, treatmentData)).quantity)
            }


            container.append(medicine_element, quantity_element)
            treatment_div_element.appendChild(container)
        }
    }
    if (inventory_list.length > 0) {
        const add_more_btn = get_add_more_btn()
        treatment_div_element.appendChild(add_more_btn)
    }

    return treatment_div_element
}
