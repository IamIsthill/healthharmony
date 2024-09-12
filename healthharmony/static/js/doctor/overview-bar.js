// Get department bar data based on active filter button
export function get_department_bar_data(department_data) {
    const btn = document.querySelector('.js-department-bar-btn-active');
    const filter = btn.getAttribute('data-category');

    return department_data[filter];
} // Create the department bar canvas
export function create_department_bar_canvas(filtered_department_data) {
    const departmentBarSpace = document.getElementById('departmentBars')
    let html = ''
    for (const department of filtered_department_data) {
        html += `
            <div class="barsTop">
                <h5>${department.name}</h5>
                <h2>${department.count}</h2>
            </div>
            <div>
                <div class="bars js-department-bars-border">
                    <canvas id="department-bar-${department.id}"></canvas>
                </div>
            </div>
        `
    }
    departmentBarSpace.innerHTML = html
}
// Find each canvas and create the bars
export function create_department_bars(departments, createBars) {
    let maxCount = 0
    for (const department of departments) {
        maxCount += department.count
    }
    for (const department of departments) {
        const departmentBar = document.getElementById(`department-bar-${department.id}`)
        createBars(departmentBar, maxCount, department.count)
    }
}
export function get_department_names_and_counts(filtered_department_data, department_names) {
    let prepared_data = []
    for (const key of Object.keys(filtered_department_data)) {
        const department_name = get_department_details(key, department_names)
        const data = filtered_department_data[key][department_name]
        let max_count = 0
        for (const count of Object.values(data)) {
            max_count += count.length
        }
        prepared_data.push({
            'id': key,
            'name': department_name,
            'count': max_count
        })
    }
    return prepared_data
}
// Get department name based on the key
function get_department_details(key, department_names) {
    for (const department of department_names) {
        if (parseInt(department.id) == parseInt(key)) {
            return department.department
        }
    }
    return null
}
