export function getParamsThenCreateMorbidityChart(getCountsAndLabelsForChart, categoryData, createChart) {
    try {
        const {
            filter,
            id,
            categoryName
        } = getCategoryDataParams(categoryData)
        const data = categoryData[filter][id][categoryName]
        const [labels, counts] = getCountsAndLabelsForChart(data)
        createMorbidityChart(labels, counts, categoryName, createChart)

    } catch (e) {
        console.error(e)
    }

}

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

export function getCategoryDataParams(categoryData) {
    const filter = getCategoryFilter()
    const id = getSelectedCategoryId()
    const categoryName = getCategoryName(id, filter, categoryData)
    return {
        filter,
        id,
        categoryName
    }
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
}


export function createMorbidityBarCanvas(categories) {
    const morbidityBarSpace = document.getElementById('morbidityBars')
    let html = ''
    try {
        for (const category of categories) {
            html += `
                <div>
                    <div class="barsTop">
                        <div class="info-bar">
                        <h5>${category.name}</h5>
                        <span class="material-symbols-outlined">
                            info
                            </span>
                        </div>
                        <h2>${category.count}</h2>
                    </div>
                    <div class="bars">
                        <canvas id="category-bar-${category.id}"></canvas>
                    </div>
                </div>
            `
        }
    } catch(error) {
        console.error(error)
    }

    morbidityBarSpace.innerHTML = html
}

export function selectEachMorbidityBarThenCreateBars(categories, createBars) {
    let maxCount = 0
    try{
        for (const category of categories) {
            maxCount += category.count
        }
        for (const category of categories) {
            const morbidityBar = document.getElementById(`category-bar-${category.id}`)
            createBars(morbidityBar, maxCount, category.count)
        }
    } catch(error) {
        console.error(error)
    }

}
