import {
    createChart,
} from '/static/js/utils.js'

const department_data = JSON.parse(document.getElementById('department_data').textContent)
const illness_category_data = JSON.parse(document.getElementById('illness_category_data').textContent)

console.log(department_data)
console.log(illness_category_data)

/** MAINNNNNN */

/** CATEGORIES BARS */
create_illness_category_bar_chart()

/** COLLEGE BARS */
create_colleges_bar_chart()

/** CASES TABLE */
handle_onclick_review_btn()

/** MAINNNNNN */



/** DEFINE FUNCTIONS BELOW */

/** CASES TABLE */

// Redirect when clicking the review button
function handle_onclick_review_btn() {
    const btns = document.querySelectorAll('.js-view-illness')

    for (const btn of btns) {
        btn.addEventListener('click', () => {
            const patient_id = btn.getAttribute('data-patient-id')
            const redirect_url = `/doctor/patient/${patient_id}`

            window.location.pathname = redirect_url
        })
    }
}

/** CATEGORIES BARS */

// Create the category bars
function create_illness_category_bar_chart() {
    // Point to the canvas in the html
    const canvas = document.getElementById('js_illness_categories_bar')
    const ctx = canvas.getContext('2d')

    // Get the labels and counts
    const {
        labels,
        counts
    } = get_labels_and_counts_category_bar(illness_category_data)

    const chartType = 'bar'
    const chartData = {
        labels: labels,
        datasets: [{
            data: counts,
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(255, 205, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(201, 203, 207, 0.2)'
            ],
            borderColor: [
                'rgb(255, 99, 132)',
                'rgb(255, 159, 64)',
                'rgb(255, 205, 86)',
                'rgb(75, 192, 192)',
                'rgb(54, 162, 235)',
                'rgb(153, 102, 255)',
                'rgb(201, 203, 207)'
            ],
            borderWidth: 1
        }]
    }

    const chartOptions = {
        plugins: {
            legend: {
                display: false,
                labels: {
                    font: {
                        family: 'Poppins', // Your custom font family
                        size: 14, // Font size
                        weight: 'normal', // Font weight
                        style: 'normal' // Font style
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false // This removes the grid lines on the x-axis
                },
                ticks: {
                    font: {
                        family: 'Arial', // Web-safe font
                        size: 10,
                        weight: 'bold',
                        style: 'normal'
                    }
                }
            },
            y: {
                beginAtZero: true, // Ensure y-axis starts from 0
                display: false
            }
        }
    }
    createChart(ctx, chartType, chartData, chartOptions)
}

function get_labels_and_counts_category_bar(illness_category_data) {
    let labels = []
    let counts = []
    for (const category of illness_category_data) {
        labels.push(category.category_name)
        counts.push(category.cases_count)
    }

    return {
        'labels': labels,
        'counts': counts
    }
}

/** COLLEGE BARS */
function get_labels_and_counts_college_bar(department_data) {
    let labels = []
    let counts = []
    for (const department of department_data) {
        labels.push(department.department_name)
        counts.push(department.cases_count)
    }

    return {
        'labels': labels,
        'counts': counts
    }
}

// Create the colleges bars
function create_colleges_bar_chart() {
    // Point to the canvas in the html
    const canvas = document.getElementById('js_college_bar')
    const ctx = canvas.getContext('2d')

    // Get the labels and counts
    const {
        labels,
        counts
    } = get_labels_and_counts_college_bar(department_data)

    const chartType = 'bar'
    const chartData = {
        labels: labels,
        datasets: [{
            data: counts,
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(255, 205, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(201, 203, 207, 0.2)'
            ],
            borderColor: [
                'rgb(255, 99, 132)',
                'rgb(255, 159, 64)',
                'rgb(255, 205, 86)',
                'rgb(75, 192, 192)',
                'rgb(54, 162, 235)',
                'rgb(153, 102, 255)',
                'rgb(201, 203, 207)'
            ],
            borderWidth: 1
        }]
    }

    const chartOptions = {
        plugins: {
            legend: {
                display: false,
                labels: {
                    font: {
                        family: 'Poppins', // Your custom font family
                        size: 14, // Font size
                        weight: 'normal', // Font weight
                        style: 'normal' // Font style
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false // This removes the grid lines on the x-axis
                },
                ticks: {
                    font: {
                        family: 'Arial', // Web-safe font
                        size: 10,
                        weight: 'bold',
                        style: 'normal'
                    }
                }
            },
            y: {
                beginAtZero: true, // Ensure y-axis starts from 0
                display: false
            }
        }
    }
    createChart(ctx, chartType, chartData, chartOptions)
}
