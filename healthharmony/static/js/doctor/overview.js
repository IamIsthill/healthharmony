import {
    create_morbidity_chart,
    get_active_illness,
    get_active_illness_category_filter,
    get_illness_chart_data
} from './overview-chart.js'
import {
    getCountsAndLabelsForChart,
    createChart,
    createBars,
    getCurrentUrl
} from '../utils.js'

import {
    create_department_bar_canvas,
    create_department_bars,
    get_department_bar_data,
    get_department_names_and_counts
} from './overview-bar.js';


const illness_data = JSON.parse(document.getElementById('illness_data').textContent)
const department_names = JSON.parse(document.getElementById('department_names').textContent)
const department_data = JSON.parse(document.getElementById('department_data').textContent)
const sorted_illness_category = JSON.parse(document.getElementById('sorted_illness_category').textContent)

/** Illness Table */
handle_onclick_review_illness()
handle_onclick_illness_status()


/** Illness Category Chart */
get_init_params_create_morbidity_chart()
handle_onclick_illness_dates()
handle_onchange_illness_category()

/** Department Bars */
create_department_bars_based_active_params()
handle_onclick_department_filters()

/** Illness Table */

// Update table when user clicks the different illness status
function handle_onclick_illness_status() {
    const btns = document.querySelectorAll('.js-illness-filter')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            for (const btn of btns) {
                btn.classList.remove('js-illness-filter-active')
                btn.classList.remove('button_cat-active')
            }

            btn.classList.add('js-illness-filter-active')
            btn.classList.add('button_cat-active')
            const filtered_illness_data = get_filtered_illness_data()
            const paginated_data = paginateArray(filtered_illness_data)
            update_illness_table(paginated_data)
            handle_onclick_review_illness()
        })
    }
}


//When user clicks review on illness, redirect to patient-profile
function handle_onclick_review_illness() {
    const btns = document.querySelectorAll('.js-view-illness')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            const patient_id = btn.getAttribute('data-patient-id')
            const go_to = `/doctor/patient/${patient_id}/`
            const url = new URL(window.location.href)
            url.pathname = go_to
            window.location.href = url
        })
    }
}

// get filtered data based on current illness status
function get_filtered_illness_data() {
    const btn = document.querySelector('.js-illness-filter-active')
    const filter = btn.getAttribute('data-category').toLowerCase()

    let filtered_data = []
    if (filter == 'all') {
        filtered_data = illness_data
    } else {
        for (const illness of illness_data) {
            if (filter == 'not' && (illness.diagnosis == '' || !illness.diagnosis)) {
                filtered_data.push(illness)
            } else if (filter == 'done' && (illness.diagnosis != '' || illness.diagnosis)) {
                filtered_data.push(illness)
            }
        }
    }

    return filtered_data
}

// Update the illness table
function update_illness_table(filtered_illness_data) {
    const illness_body_element = document.getElementById('illness_body')
    illness_body_element.innerHTML = ''
    if (filtered_illness_data.length <= 0) {
        illness_body_element.innerHTML = '<td colspan="4">Congratulations! No case as of this moment.</td>'
    } else {


        for (const illness of filtered_illness_data) {
            const case_status = illness.diagnosis ? 'Completed' : 'Pending'


            let patient = ''

            if(illness.patient_first_name && illness.patient_last_name) {
                patient = `${illness.patient_first_name} ${illness.patient_last_name}`

            }
            else {
                patient = `${illness.patient_email}`
            }
            illness_body_element.innerHTML += `
            <tr>
              <td class = "table-data name-column">
                <span class="patient btn" data-patient-id="${illness.patient}">${patient}</span>
              </td>
              <td class = "table-data issue-column">${illness.issue}</td>
              <td class = "table-data status-column">${case_status}</td>
              <td class="js-view-illness btn table-data view-column" data-patient-id="${illness.patient}">Review</td>
            </tr>
        `
        }
    }


}


/** Illness Category Chart */


// When user changes the illness category
function handle_onchange_illness_category() {
    const select_element = document.querySelector('.js_illness_category')

    select_element.addEventListener('change', () => {
        get_init_params_create_morbidity_chart()
    })
}

// Update chart when clicking on the illness date filters
function handle_onclick_illness_dates() {
    const btns = document.querySelectorAll('.js_category_filter')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            for (const btn of btns) {
                btn.classList.remove('js_category_filter_active')
                btn.classList.remove('active-cat')
            }
            btn.classList.add('js_category_filter_active')
            btn.classList.add('active-cat')
            get_init_params_create_morbidity_chart()
        })
    }
}

// Gets params and create the morbidity chart
function get_init_params_create_morbidity_chart() {
    try {

        const filter = get_active_illness_category_filter()
        const illness_id = get_active_illness()
        const illness_chart_data = get_illness_chart_data(filter, illness_id, sorted_illness_category)
        const illness_category_name = illness_chart_data[0]
        const [labels, counts] = getCountsAndLabelsForChart(illness_chart_data[1])

        create_morbidity_chart(labels, counts, illness_category_name, createChart)

    } catch (error) {
        console.error(error.message)
    }
}


/** Department Bars */

// When user clicks the date filters in departments
function handle_onclick_department_filters() {
    const btns = document.querySelectorAll('.js-department-bar-btn')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            for (const btn of btns) {
                btn.classList.remove('js-department-bar-btn-active')
                btn.classList.remove('bar-btn-active')
            }
            btn.classList.add('js-department-bar-btn-active')
            btn.classList.add('bar-btn-active')
            create_department_bars_based_active_params()
            add_border_then_remove_to_bars()

        })
    }
}

// Add border thingy to indicate change
function add_border_then_remove_to_bars() {
    const bar_elements = document.querySelectorAll('.js-department-bars-border')

    for (const bar_element of bar_elements) {
        bar_element.classList.add('border')
    }
    setTimeout(() => {
        for (const bar_element of bar_elements) {
            bar_element.classList.remove('border');
        }
    }, 1000);

}

// Get the current params then create the department bars
function create_department_bars_based_active_params() {
    const filtered_department_data = get_department_bar_data(department_data)
    const department_name_with_count = get_department_names_and_counts(filtered_department_data, department_names)
    create_department_bar_canvas(department_name_with_count)
    create_department_bars(department_name_with_count, createBars)
}


// Get current page and then paginate array
function paginateArray(array) {
    const url = getCurrentUrl()

    let page = url.searchParams.get('page')
    if (!page) {
        page = 1
    }

    page = parseInt(page)
    let itemStart = page * 10 - 9
    let itemEnd = page * 10
    if (itemStart > array.length) {
        page = Math.ceil(array.length / 10)
        itemStart = page * 10 - 9
        itemEnd = page * 10

    }
    let paginatedArray = []

    for (let key in array) {
        key = parseInt(key)
        if (key + 1 >= itemStart && key + 1 <= itemEnd) {
            paginatedArray.push(array[key])
        }
    }
    return paginatedArray
}
