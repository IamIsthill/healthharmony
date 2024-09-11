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
    try {
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
    } catch (error) {
        console.error(error)
    }


}

export function createBars(bar, maxCount, value) {
    try {
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
    } catch (error) {
        console.error(error)
    }
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

export function openPopup(modal) {
    modal.classList.add('open-popup')
}

export function closePopup(modal) {
    modal.classList.remove('open-popup')
}

export function getCurrentUrl() {
    const url = new URL(window.location.href)
    return url
}

export function paginateArray(array, page) {
    if (!page) {
        page = 1
    }

    page = parseInt(page)
    let itemStart = page * 10 - 9
    let itemEnd = page * 10
    if (itemStart > array.length) {
        page = Math.ceil(array.length / 10)
        itemStart = page * 10 - 9
        itemEnd = page * 10

    }
    let paginatedArray = []

    for (let key in array) {
        key = parseInt(key)
        if (key + 1 >= itemStart && key + 1 <= itemEnd) {
            paginatedArray.push(array[key])
        }
    }
    return paginatedArray
}

export function saveItem(key, value) {
    value = JSON.stringify(value)
    localStorage.setItem(key, value)
}

export function getItem(key) {
    let item = localStorage.getItem(key)
    return JSON.parse(item)
}

export function removeItem(key) {
    localStorage.removeItem(key)
}

export function getToken() {
    const inputs = document.querySelectorAll('input')
    let token = null
    for (const input of inputs) {
        const inputName = input.getAttribute('name')
        if (inputName == 'csrfmiddlewaretoken') {
            token = input.value
        }
    }
    return token
}

export function listenToEnter(logicAfterEnter) {
    document.addEventListener('keypress', (event) => {
        if (event.key == 'Enter') {
            logicAfterEnter()
        }
    })
}

export function getElapsedTime(dateString) {
    const now = Date.now();
    const elapsedTimeInMilliseconds = now - new Date(dateString).getTime();
    const totalSeconds = Math.floor(elapsedTimeInMilliseconds / 1000);
    const elapsed = {}
    if (totalSeconds > 60) {
        elapsed.seconds = totalSeconds % 60
        const minutes = Math.floor(totalSeconds / 60)
        if (minutes > 60) {
            elapsed.minutes = minutes % 60
            const hours = Math.floor(minutes / 60)
            if (hours > 24) {
                elapsed.hours = hours % 60
                elapsed.days = Math.floor(hours / 24)
            } else {
                elapsed.hours = hours
            }
        } else {
            elapsed.minutes = minutes
        }
    } else {
        elapsed.seconds = totalSeconds
    }
    let stmt = ''
    if (elapsed.seconds)(
        stmt = `${elapsed.seconds}s `
    )
    if (elapsed.minutes) {
        stmt = `${elapsed.minutes}m ${elapsed.seconds}s`
    }
    if (elapsed.hours) {
        stmt = `${elapsed.hours}hr ${elapsed.minutes}m ${elapsed.seconds}s`
    }
    if (elapsed.days) {
        stmt = `${elapsed.days}d ${elapsed.hours}hr ${elapsed.minutes}m ${elapsed.seconds}s`
    }
    return stmt
}

export function formatDate(dateString) {

    const formattedDate = new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
    })
    return formattedDate

}
