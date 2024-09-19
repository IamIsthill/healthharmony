export function getDepartmentFilter() {
    const activeDepartmentFilter = document.querySelector('.active-department-filter')
    const filter = activeDepartmentFilter.getAttribute('data-patient-data').toLowerCase()
    return filter
}

export function getDepartmentId() {
    // const activeDepartment = document.querySelector('.active-department-selector')
    const departmentNames = document.querySelector('.js-department-names')
    const id = departmentNames.value
    return parseInt(id)
}

export function getDepartmentName(departments, id) {
    for (const department of departments) {
        if (parseInt(department.id) == id) {
            return department.department
        }
    }
}

export function getDepartmentDataParams(departments) {
    const filter = getDepartmentFilter()
    const id = getDepartmentId()
    const department = getDepartmentName(departments, id)
    return {
        filter,
        id,
        department
    }
}

export function getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart,
    createChart) {
    try {
        const {
            filter,
            id,
            department
        } = getDepartmentDataParams(departments)
        const data = departmentData[filter][id][department]
        const [labels, counts] = getCountsAndLabelsForChart(data)
        createDepartmentChart(labels, counts, department, createChart)

    } catch (error) {
        console.error(`No data for department chart: ${error.message}`)
    }
}


export function createDepartmentChart(labels, counts, department, createChart) {
    const canvas = document.getElementById('departmentChart')
    const ctx = canvas.getContext('2d')

    const chartType = 'line'
    const chartData = {
        labels: labels,
        datasets: [{
            label: department,
            data: counts,
            borderWidth: 1,
            indexAxis: 'x',
            backgroundColor: 'rgba(238, 172, 19, 0.2)', // Simplified background color for line chart
            borderColor: 'rgba(238, 172, 19, 1)', // Adding border color for better visualization
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

export function createDepartmentBarCanvas(departments) {
    const departmentBarSpace = document.getElementById('departmentBars')
    let html = ''
    for (const department of departments) {
        html += `
            <div class="barsTop">   
                <h5>${department.name}</h5>
                <h2>${department.count}</h2>
            </div>
                <div class="bars">
                    <canvas id="department-bar-${department.id}"></canvas>
                </div>
            </div>
        `
    }
    departmentBarSpace.innerHTML = html
}

export function selectEachDepartmentBarThenCreateBars(departments, createBars) {
    let maxCount = 0
    for (const department of departments) {
        maxCount += department.count
    }
    for (const department of departments) {
        const departmentBar = document.getElementById(`department-bar-${department.id}`)
        createBars(departmentBar, maxCount, department.count)
    }
}
