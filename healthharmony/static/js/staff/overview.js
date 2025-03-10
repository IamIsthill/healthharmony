import {
    getParamsThenCreateMorbidityChart,
    createMorbidityBarCanvas,
    selectEachMorbidityBarThenCreateBars
} from './overview-morbidity.js'
import {
    getParamsThenCreateDepartmentChart,
    createDepartmentBarCanvas,
    selectEachDepartmentBarThenCreateBars
} from './overview-department.js'
import {
    getCountsAndLabelsForChart,
    createChart,
    getBarCounts,
    createBars,
    openModal,
    closeModal
} from '../utils.js'
const categoryData = JSON.parse(document.getElementById('categoryS').textContent)
const departmentData = JSON.parse(document.getElementById('sorted-department').textContent)
const departments = JSON.parse(document.getElementById('departments').textContent)
const category_data = JSON.parse(document.getElementById('category_data').textContent)

main()

function main() {




    /**
     * MAIN CODE
     */
    // listenToError()
    // listenToSuccess()
    // listenToModalOk()

    // SHORTCUTS
    listenCheckBed()
    listenToAddVisitBtn()
    handle_add_new_patient_btn()
    handle_onclick_ambulance()
    handle_onclick_wheelchairs()

    listenToCategoryFilterBtns()
    listenToCategorySelector()
    getParamsThenCreateMorbidityChart(getCountsAndLabelsForChart, categoryData, createChart)

    listenToDepartmentsFilterBtns()
    listenToDepartmentSelector()
    getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart, createChart)

    listenToCategoryBarFilters()
    createMorbidityBarCanvas(getBarCounts(categoryData['yearly']))
    selectEachMorbidityBarThenCreateBars(getBarCounts(categoryData['yearly']), createBars)
    handle_hover_illness_info()

    listenToDepartmentBarFilters()
    createDepartmentBarCanvas(getBarCounts(departmentData['yearly']))
    selectEachDepartmentBarThenCreateBars(getBarCounts(departmentData['yearly']), createBars)
}

// when user hovers on the info icon on the morbidity bars
function handle_hover_illness_info() {
    const icons = document.querySelectorAll('.js_view_categories');

    // Exit early if there are no icons
    if (icons.length === 0) {
        return;
    }

    for (const icon of icons) {
        icon.addEventListener('mouseenter', () => {
            const category_id = parseInt(icon.getAttribute('category-id'));
            const category = get_category(category_id);

            // Get the bounding box of the icon relative to the sticky container
            const rightPart = document.querySelector('.right-part');
            const rightPartRect = rightPart.getBoundingClientRect();
            const iconRect = icon.getBoundingClientRect();

            // Calculate position relative to `.right-part`
            const offsetTop = iconRect.top - rightPartRect.top;
            const offsetLeft = iconRect.left - rightPartRect.left;

            // Create the hover div
            const hover_div = document.createElement('div');
            hover_div.classList.add('js_hover_illness_info');
            hover_div.innerHTML = `
                <h4 class="hover-title">${category.category}</h4>
                <p class="hover-info">${category.description}</p>
            `;

            
            rightPart.appendChild(hover_div);

            
            const hoverWidth = hover_div.offsetWidth;
            const hoverHeight = hover_div.offsetHeight;

            
            hover_div.style.position = 'absolute';
            hover_div.style.top = `${offsetTop + iconRect.height / 2 - hoverHeight / 2 - 150}px`; 
            hover_div.style.left = `${offsetLeft - hoverWidth + 70}px`; 
            hover_div.style.zIndex = 100;
            hover_div.style.background = 'white';
            hover_div.style.border = '1px solid #ccc';
            hover_div.style.padding = '8px';
            hover_div.style.borderRadius = '4px';
            hover_div.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.15)';
            hover_div.style.width = '300px';
            hover_div.style.wordWrap = 'break-word';

            
            icon.addEventListener('mouseleave', () => {
                hover_div.remove();
            });
        });
    }
}





function get_category(id) {
    if (category_data.length == 0) {
        return null
    }

    for (const category of category_data) {
        if (parseInt(id) == category.id) {
            return category
        }
    }

    return null

}

//Staff clicks checks wheelchairs
function handle_onclick_wheelchairs() {
    const btn = document.querySelector('.js-check-wheel')

    btn.addEventListener('click', () => {
        const modal = document.querySelector('.js_check_wheelchair_modal')
        const close_btns = document.querySelectorAll('.js_close_check_wheelchair_modal')

        // Open the modal
        openModal(modal)

        //Iterate close btn, add event listener to close modal
        for (const close of close_btns) {
            closeModal(modal, close)

            // reset the form if close was clicked
            close.addEventListener('click', () => {
                const form = document.querySelector('.js_wheelchair_form')
                form.reset()
            })
        }

        //
        prevent_invalid_number_wheelchair_field()
    })
}

// Prevent invalid input in the wheelchair number field
function prevent_invalid_number_wheelchair_field() {
    const wheelchairInputs = document.querySelectorAll('#available_wheelchairs, #unavailable_wheelchairs');

    wheelchairInputs.forEach(input => {
        // Prevent 'e', '-', and other invalid characters from being typed in the field
        input.addEventListener('keydown', function(e) {
            if (['e', 'E', '-'].includes(e.key)) {
                e.preventDefault();
            }
        });

        // Prevent pasting invalid characters
        input.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');

            if (parseInt(this.value) > parseInt(this.getAttribute('max'))) {
                this.value = parseInt(this.getAttribute('max'))
            }
        });
    });
}

// Staff clicks the check ambulance
function handle_onclick_ambulance() {
    const btn = document.querySelector('.js-check-ambulance')

    btn.addEventListener('click', () => {
        const modal = document.querySelector('.js_check_ambulance_modal')
        const close_btns = document.querySelectorAll('.js_close_check_ambulance_modal')
        openModal(modal)

        for (const close of close_btns) {
            closeModal(modal, close)
        }

    })
}

function handle_add_new_patient_btn() {
    const btn = document.querySelector('.js-add-patient')

    btn.addEventListener('click', () => {
        const modal = document.getElementById('js_add_patient_modal')
        const close_btns = document.querySelectorAll('.js_close_add_patient_modal')

        openModal(modal)

        const patientBday = document.querySelector('.js-patient-bday')
        patientBday.addEventListener('input', () => {
            const bday = new Date(patientBday.value)
            const currentDate = new Date()

            if (bday > currentDate) {
                const year = currentDate.getFullYear()
                const month = String(currentDate.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
                const dd = String(currentDate.getDate()).padStart(2, '0');
                patientBday.value = `${year}-${month}-${dd}`; 
            }
        })

        for (const btn of close_btns) {
            closeModal(modal, btn)

            // Reset the form when closed
            btn.addEventListener('click', () => {
                const form = document.querySelector('.js_add_patient_form')
                form.reset()
            })
        }

    })
}

function listenCheckBed() {
    const checkBedBtn = document.querySelector('.js-check-bed')

    checkBedBtn.addEventListener('click', () => {
        const bedModal = document.querySelector('.js-check-bed-modal')
        openModal(bedModal)

        const close_btns = document.querySelectorAll('.js_close_check_bed_modal')

        for (const close of close_btns) {
            closeModal(bedModal, close)
        }
    })

}

function listenToError() {
    try {
        const errorModal = document.querySelector('.js-error-modal')
        errorModal.classList.add('open-popup-visit')
    } catch (error) {
        console.error(error.message)
    }
}

function listenToSuccess() {
    try {
        const successModal = document.querySelector('.js-success-modal')
        successModal.classList.add('open-popup-visit')
    } catch (error) {
        console.error(error.message)
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
    } catch (error) {
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
            getParamsThenCreateDepartmentChart(departments, departmentData, getCountsAndLabelsForChart,
                createChart)
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
            createMorbidityBarCanvas(getBarCounts(categoryData[filter]))
            selectEachMorbidityBarThenCreateBars(getBarCounts(categoryData[filter]), createBars)
            handle_hover_illness_info()
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
            createDepartmentBarCanvas(getBarCounts(departmentData[filter]))
            selectEachDepartmentBarThenCreateBars(getBarCounts(departmentData[filter]), createBars)
            handle_hover_illness_info()
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
