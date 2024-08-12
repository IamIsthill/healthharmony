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
