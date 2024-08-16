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

export function getBarCounts(mainData) {
    let barCounts = []
    for (const [id, name] of Object.entries(mainData)) {
        for (const [dataName, data] of Object.entries(name)) {
            let count = 0
            for (const [dates, cases] of Object.entries(data)) {
                count += cases.length
            }
            barCounts.push({
                'count': count,
                'name': dataName,
                'id': id
            })
        }
    }
    return barCounts

}

export function createBars(bar, maxCount, value) {
    const canvas = bar;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    canvas.width = 0
    canvas.height = 0
    canvas.width = canvas.parentElement.clientWidth || 100; // Fallback value
    canvas.height = canvas.parentElement.clientHeight || 100;

    //background bar
    ctx.fillStyle = '#E4E7EC'
    ctx.fillRect(0, 0, parseInt(canvas.width), parseInt(canvas.height))

    //foreground bar
    ctx.fillStyle = '#FFDA80'
    let width = (parseInt(canvas.width)) / maxCount * (parseInt(value))
    ctx.fillRect(0, 0, width, parseInt(canvas.height))
    // console.log('Canvas width:', canvas.width, 'Canvas height:', canvas.height);
}

export function getActiveFilter(filterClassName, sorterName) {
    const activeFilterBtn = document.querySelector(`.${filterClassName}`)
    const filter = activeFilterBtn.getAttribute(sorterName)
    return filter
}

export function openModal(modal) {
    modal.style.display = "block";
}

export function closeModal(modal, btn) {
    btn.addEventListener('click', (event) => {
        event.preventDefault()
        modal.style.display = "none";
    })
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}
