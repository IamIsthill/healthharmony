import {
    create_department_bar_canvas,
    create_department_bars,
    get_department_bar_data,
    get_department_names_and_counts
} from '/static/js/doctor/overview-bar.js'
import {
    create_morbidity_chart,
    get_active_illness,
    get_active_illness_category_filter,
    get_illness_chart_data
} from '/static/js/doctor/overview-chart.js'
import {
    getCountsAndLabelsForChart,
    createChart,
    getBarCounts,
    createBars,
    openModal,
    closeModal
} from '/static/js/utils.js'

const illness_data = JSON.parse(document.getElementById('illness_data').textContent)
const department_names = JSON.parse(document.getElementById('department_names').textContent)
const department_data = JSON.parse(document.getElementById('department_data').textContent)
const sorted_illness_category = JSON.parse(document.getElementById('sorted_illness_category').textContent)

console.log(illness_data)
console.log(department_names)
console.log(department_data)
console.log(sorted_illness_category)

/** Illness Table */


/** Illness Category Chart */
get_init_params_create_morbidity_chart()
handle_onclick_illness_dates()
handle_onchange_illness_category()

/** Department Bars */
create_department_bars_based_active_params()
handle_onclick_department_filters()

/** Illness Table */

//When user clicks review on illness, redirect to patient-profile
function handle_onclick_review_illness() {
    const btns = document.querySelectorAll('.js-view-illness-btn')

    for (const btn of btns) {

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
            }
            btn.classList.add('js_category_filter_active')
            get_init_params_create_morbidity_chart()
        })
    }
}

// Gets params and create the morbidity chart
function get_init_params_create_morbidity_chart() {
    const filter = get_active_illness_category_filter()
    const illness_id = get_active_illness()
    const illness_chart_data = get_illness_chart_data(filter, illness_id, sorted_illness_category)
    const illness_category_name = illness_chart_data[0]
    const [labels, counts] = getCountsAndLabelsForChart(illness_chart_data[1])

    create_morbidity_chart(labels, counts, illness_category_name, createChart)
}


/** Department Bars */

// When user clicks the date filters in departments
function handle_onclick_department_filters() {
    const btns = document.querySelectorAll('.js-department-bar-btn')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            for (const btn of btns) {
                btn.classList.remove('.js-department-bar-btn-active')
            }
            btn.classList.add('.js-department-bar-btn-active')
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
