// Get the current active illness category filter button
export function get_active_illness_category_filter() {
    const active_filter_btn = document.querySelector('.js_category_filter_active');
    const active_filter = active_filter_btn.getAttribute('data-category');

    return active_filter.toLowerCase();
} // Get the current active illness category
export function get_active_illness() {
    const active_illness = document.querySelector('.js_illness_category')
    return active_illness.value
}
export function get_illness_chart_data(filter, illness_id, sorted_illness_category) {
    try {

        const illness_chart_data = sorted_illness_category[filter][illness_id]
        return Object.entries(illness_chart_data)[0]
    } catch {
        return null
    }

}
export function create_morbidity_chart(labels, counts, categoryName, createChart) {
    try {
        const canvas = document.getElementById('morbidityChart')
        const ctx = canvas.getContext('2d')

        const chartType = 'line'
        const chartData = {
            labels: labels,
            datasets: [{
                label: categoryName,
                data: counts,
                borderWidth: 2,
                indexAxis: 'x',
                backgroundColor: 'rgba(255, 45, 25, 0.2)', // Simplified background color for line chart
                borderColor: 'rgba(255, 45, 25, 1)', // Adding border color for better visualization
                fill: false,
                tension: 0.5
            }]
        }
        const chartOptions = {
            plugins: {
                legend: {
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
                y: {
                    beginAtZero: true, // Ensure y-axis starts from 0
                }
            }
        }

        createChart(ctx, chartType, chartData, chartOptions)
    } catch (error) {
        console.error(error.message)
    }
}
