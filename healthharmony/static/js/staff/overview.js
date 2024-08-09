import {
    getParamsThenCreateMorbidityChart,
    createMorbidityBarCanvas,
    selectEachMorbidityBarThenCreateBars
} from '/static/js/staff/morbidity.js'
import {
    getParamsThenCreateDepartmentChart,
    createDepartmentBarCanvas,
    selectEachDepartmentBarThenCreateBars
} from '/static/js/staff/department.js'
import {
    getCountsAndLabelsForChart,
    createChart,
    getBarCounts,
    createBars
} from '/static/js/utils.js'
const categoryData = JSON.parse(document.getElementById('categoryS').textContent)
const departmentData = JSON.parse(document.getElementById('sorted-department').textContent)
const departments = JSON.parse(document.getElementById('departments').textContent)

main()

function main() {
    listenToAddVisitBtn()

    listenToCategoryFilterBtns()
    listenToCategorySelector()
    getParamsThenCreateMorbidityChart(getCountsAndLabelsForChart, categoryData, createChart)

    listenToDepartmentsFilterBtns()
    listenToDepartmentSelector()
    getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart, createChart)

    listenToCategoryBarFilters()
    createMorbidityBarCanvas(getBarCounts(categoryData['yearly']))
    selectEachMorbidityBarThenCreateBars(getBarCounts(categoryData['yearly']), createBars)

    listenToDepartmentBarFilters()
    createDepartmentBarCanvas(getBarCounts(departmentData['yearly']))
    selectEachDepartmentBarThenCreateBars(getBarCounts(categoryData['yearly']), createBars)


}


function listenToCategoryFilterBtns() {
    const categoryFilterBtns = document.querySelectorAll('.categoryDateFilter')

    for (const btn of categoryFilterBtns) {

        btn.addEventListener('click', () => {
            for (const btn of categoryFilterBtns) {
                btn.classList.remove('active-category-filter')
                btn.classList.remove('active-cat')
            }

            btn.classList.add('active-category-filter')
            btn.classList.add('active-cat')

            getParamsThenCreateMorbidityChart(getCountsAndLabelsForChart, categoryData, createChart)
        })
    }
}


function listenToCategorySelector() {
    const categorySelector = document.getElementById('categories')
    categorySelector.addEventListener('change', () => {
        getParamsThenCreateMorbidityChart(getCountsAndLabelsForChart, categoryData, createChart)
    })
}


function listenToDepartmentsFilterBtns() {
    const departmentFilterBtns = document.querySelectorAll('.departmentDateFilter')
    for (const btn of departmentFilterBtns) {
        btn.addEventListener('click', () => {
            for (const btn of departmentFilterBtns) {
                btn.classList.remove('active-department-filter')
                btn.classList.remove('active-pat')
            }
            btn.classList.add('active-department-filter')
            btn.classList.add('active-pat')
            getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart, createChart)
        })
    }
}

function listenToDepartmentSelector() {
    const departmentSelectorBtns = document.querySelectorAll('.departmentNames')
    for (const btn of departmentSelectorBtns) {
        btn.addEventListener('click', () => {
            for (const btn of departmentSelectorBtns) {
                btn.classList.remove('active-department-selector')
            }
            btn.classList.add('active-department-selector')
            getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart, createChart)
        })
    }
}

function listenToCategoryBarFilters() {
    const categoryBarBtns = document.querySelectorAll('.js-category-bar-btn')
    for (const btn of categoryBarBtns) {
        btn.addEventListener('click', () => {
            for (const btn of categoryBarBtns) {
                btn.classList.remove('js-category-bar-filter-btn')
            }
            btn.classList.add('js-category-bar-filter-btn')
            const filter = btn.getAttribute('data-category-data')
            selectEachMorbidityBarThenCreateBars(getBarCounts(categoryData[filter]), createBars)
        })
    }
}

function listenToDepartmentBarFilters() {
    const departmentBarBtns = document.querySelectorAll('.js-department-bar-btn')
    for (const btn of departmentBarBtns) {
        btn.addEventListener('click', () => {
            for (const btn of departmentBarBtns) {
                btn.classList.remove('js-department-bar-filter-btn')
            }
            btn.classList.add('js-department-bar-filter-btn')
            const filter = btn.getAttribute('data-category-data')
            selectEachDepartmentBarThenCreateBars(getBarCounts(categoryData[filter]), createBars)
        })
    }
}

function listenToAddVisitBtn() {
    const addVisitBtn = document.querySelector('.js-add-visit-btn')
    addVisitBtn.addEventListener('click', () => {
        const addVisitModal = document.getElementById('js-add-visit-modal')
        openModal(addVisitModal)
        closeModal(addVisitModal)
    })
}

function openModal(modal) {
    modal.style.display = "block";
}

function closeModal(modal) {
    const closeVisitModalBtn = document.querySelector('.js-close-add-visit-modal-btn')
    closeVisitModalBtn.addEventListener('click', () => {
        modal.style.display = "none";
    })
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}
