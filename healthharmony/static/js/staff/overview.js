import {
    getParamsThenCreateMorbidityChart,
    createMorbidityBarCanvas,
    selectEachMorbidityBarThenCreateBars
} from '/static/js/staff/overview-morbidity.js'
import {
    getParamsThenCreateDepartmentChart,
    createDepartmentBarCanvas,
    selectEachDepartmentBarThenCreateBars
} from '/static/js/staff/overview-department.js'
import {
    getCountsAndLabelsForChart,
    createChart,
    getBarCounts,
    createBars,
    openModal,
    closeModal
} from '/static/js/utils.js'
const categoryData = JSON.parse(document.getElementById('categoryS').textContent)
const departmentData = JSON.parse(document.getElementById('sorted-department').textContent)
const departments = JSON.parse(document.getElementById('departments').textContent)

main()

function main() {
    /**
     * TEST AREA
     */
    listenCheckBed()


    /**
     * MAIN CODE
     */
    listenToError()
    listenToSuccess()
    listenToModalOk()

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
    selectEachDepartmentBarThenCreateBars(getBarCounts(departmentData['yearly']), createBars)
}

function listenCheckBed() {
    const checkBedBtn = document.querySelector('.js-check-bed')

    checkBedBtn.addEventListener('click', () => {
        const bedModal = document.querySelector('.js-check-bed-modal')
        openModal(bedModal)
        window.onclick = function(event) {
            if (event.target == bedModal) {
                bedModal.style.display = "none";
            }
        }
    })

}

function listenToError() {
    try {
        const errorModal = document.querySelector('.js-error-modal')
        errorModal.classList.add('open-popup-visit')
    } catch(error) {
        console.error(error)
    }
}

function listenToSuccess() {
    try {
        const successModal = document.querySelector('.js-success-modal')
        successModal.classList.add('open-popup-visit')
    } catch(error) {
        console.error(error)
    }
}

function listenToModalOk() {
    try {
        const okBtns = document.querySelectorAll('.js-modal-btn-ok')
        for (const btn of okBtns) {
            btn.addEventListener('click', () => {
                const modal = btn.parentElement.parentElement
                modal.classList.remove('open-popup-visit')
            })
        }
    } catch(error) {
        console.error(error)
    }
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
        try {
            getParamsThenCreateMorbidityChart(getCountsAndLabelsForChart, categoryData, createChart)
        } catch (error) {
            console.log(error)
        }

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
    const departmentSelectorBtns = document.querySelector('.js-department-names')
    departmentSelectorBtns.addEventListener('change', () => {
        getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart, createChart)
    })
}

function listenToCategoryBarFilters() {
    const categoryBarBtns = document.querySelectorAll('.js-category-bar-btn')
    for (const btn of categoryBarBtns) {
        btn.addEventListener('click', () => {
            for (const btn of categoryBarBtns) {
                btn.classList.remove('js-category-bar-filter-btn')
                btn.classList.remove('bar-btn-active')
            }
            btn.classList.add('js-category-bar-filter-btn')
            btn.classList.add('bar-btn-active')
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
                btn.classList.remove('bar-btn-active')
            }
            btn.classList.add('js-department-bar-filter-btn')
            btn.classList.add('bar-btn-active')
            const filter = btn.getAttribute('data-category-data')
            selectEachDepartmentBarThenCreateBars(getBarCounts(departmentData[filter]), createBars)
        })
    }
}

function listenToAddVisitBtn() {
    const addVisitBtn = document.querySelector('.js-add-visit-btn')
    addVisitBtn.addEventListener('click', () => {
        const addVisitModal = document.getElementById('js-add-visit-modal')
        const closeVisitModalBtn = document.querySelector('.js-close-add-visit-modal-btn')
        openModal(addVisitModal)
        closeModal(addVisitModal, closeVisitModalBtn)
    })
}
