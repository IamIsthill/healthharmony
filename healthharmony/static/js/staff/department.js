export function getDepartmentFilter() {
    const activeDepartmentFilter = document.querySelector('.active-department-filter')
    const filter = activeDepartmentFilter.getAttribute('data-patient-data').toLowerCase()
    return filter
}
