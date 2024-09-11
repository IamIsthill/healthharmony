export function getCountsAndLabelsForInventoryChart(data) {
    let labels = []
    let counts = []
    for (const [key, value] of Object.entries(data)) {
        let count = 0
        if (value.length > 0) {
            for (const item of Object.values(value)) {
                count += parseInt(item['total_quantity'])
            }
        }
        labels.push(key)
        counts.push(count)
    }
    return {
        labels,
        counts
    }
}

export function getChartParams(getActiveFilter) {
    const category = getActiveFilter('js-seasonal-category-btn-active', 'data-sorter')
    const filter = getActiveFilter('js-seasonal-filter-active', 'data-sorter')
    return {
        category,
        filter
    }
}

export function createInventoryChart(labels, counts, categoryName, createChart) {
    const canvas = document.getElementById('js-seasonal-canvas')
    const ctx = canvas.getContext('2d')

    const chartType = 'line'
    const chartData = {
        labels: labels,
        datasets: [{
            label: categoryName,
            data: counts,
            borderWidth: 2,
            indexAxis: 'x',
            backgroundColor: 'rgba(32, 43, 55, 0.2)', // Simplified background color for line chart
            borderColor: 'rgba(32, 43, 55, 1)', // Adding border color for better visualization
            fill: false,
            tension: 0.5
        }]
    }
    const chartOptions = {
        // responsive: false,  // Nigga keeps shaking, maybe he's cold
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
}

export function getTrendsParams(getActiveFilter) {
    const trendFilter = getActiveFilter('js-seasonal-bar-filter-active', 'data-filter')
    const trendCategory = getActiveFilter('js-seasonal-bar-category-active', 'data-filter')
    return {
        trendCategory,
        trendFilter
    }
}

export function getInventoryItem(id, data) {
    let item = null
    for (const value of Object.values(data)) {
        if (value.length > 0) {
            for (const detailedItem of Object.values(value)) {
                if (parseInt(detailedItem.id) == parseInt(id)) {
                    item = detailedItem
                }
            }
        }
    }
    return item
}
