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

/** Illness Category Chart */
get_init_params_create_morbidity_chart()
handle_onclick_illness_dates()
handle_onchange_illness_category()


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
