export function getCountsAndLabelsForChart(data) {
    let labels = []
    let counts = []
    for (const [key, value] of Object.entries(data)) {
        labels.push(key)
        counts.push(value.length)
    }
    return [labels, counts]
}

export function createChart(ctx, chartType, chartData, chartOptions) {
    let existingChart = Chart.getChart(ctx)
    if (existingChart) {
        existingChart.destroy()
    }

    window.myChart = new Chart(ctx, {
        type: chartType,
        data: chartData,
        options: chartOptions
    })
}
