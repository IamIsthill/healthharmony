export function getDepartmentFilter() {
    const activeDepartmentFilter = document.querySelector('.active-department-filter')
    const filter = activeDepartmentFilter.getAttribute('data-patient-data').toLowerCase()
    return filter
}

export function getDepartmentId() {
    const activeDepartment = document.querySelector('.active-department-selector')
    const id = activeDepartment.getAttribute('data-department-id')
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

export function getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart, createChart) {
    const {
        filter,
        id,
        department
    } = getDepartmentDataParams(departments)
    const data = departmentData[filter][id][department]
    const [labels, counts] = getCountsAndLabelsForChart(data)
    createDepartmentChart(labels, counts, department, createChart)
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
