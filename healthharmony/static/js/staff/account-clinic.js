export function getEmployeeFilter() {
    const filter = document.querySelector('.js-employee-filters').value
    return filter
}

export function getEmployeeSearchValue() {
    const employeeSearchField = document.querySelector('.js-employee-search-field')
    return employeeSearchField.value
}

export function filterEmployeeData(employeeData, filter, searchValue) {
    let searchedEmployees = []
    for (const employee of employeeData) {
        if (parseInt(filter) == employee.access) {
            if (employee.first_name.toLowerCase().includes(searchValue) || employee.last_name.toLowerCase().includes(searchValue)) {
                searchedEmployees.push(employee)
            }
        }
        if (filter == '') {
            if (employee.first_name.toLowerCase().includes(searchValue) || employee.last_name.toLowerCase().includes(searchValue)) {
                searchedEmployees.push(employee)
            }
        }
    }
    return searchedEmployees
}
