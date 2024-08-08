export function getCategoryFilter() {
    const activeCategoryFilter = document.querySelector('.active-category-filter')
    const filter = activeCategoryFilter.getAttribute('data-category-data')
    return filter
}

export function getCategoryName(id, filter, categoryData) {
    const categoryName = categoryData[filter][id]
    return String(Object.keys(categoryName))
}

export function getSelectedCategoryId() {
    const categorySelector = document.getElementById('categories')
    const id = parseInt(categorySelector.value)
    return id
}

export function getCategoryNames(filter, categoryData) {
    let categoryNames = {}
    for (const [id, category] of Object.entries(categoryData[filter])) {
        for (const name of Object.keys(category)) {
            categoryNames[id] = name
        }
    }
    return categoryNames
}

export function createMorbidityChart(labels, counts, categoryName, createChart) {
    const canvas = document.getElementById('morbidityChart')
    const ctx = canvas.getContext('2d')

    const chartType = 'line'
    const chartData = {
        labels: labels,
        datasets: [{
            label: categoryName,
            data: counts,
            borderWidth: 1,
            indexAxis: 'x',
            backgroundColor: 'rgba(75, 192, 192, 0.2)', // Simplified background color for line chart
            borderColor: 'rgba(75, 192, 192, 1)', // Adding border color for better visualization
            fill: false,
            tension: 0.5
        }]
    }
    const chartOptions = {
        scales: {
            y: {
                beginAtZero: true // Ensure y-axis starts from 0
            }
        }
    }

    createChart(ctx, chartType, chartData, chartOptions)
}
