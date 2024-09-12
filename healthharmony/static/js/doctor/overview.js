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

get_init_params_create_morbidity_chart()

// Gets params and create the morbidity chart
function get_init_params_create_morbidity_chart() {
    const filter = get_active_illness_category_filter()
    const illness_id = get_active_illness()
    const illness_chart_data = get_illness_chart_data(filter, illness_id, sorted_illness_category)
    const illness_category_name = illness_chart_data[0]
    const [labels, counts] = getCountsAndLabelsForChart(illness_chart_data[1])

    create_morbidity_chart(labels, counts, illness_category_name, createChart)
}
