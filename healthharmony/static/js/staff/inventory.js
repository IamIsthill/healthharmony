import {
    getActiveFilter,
    openModal,
    closeModal,
    createChart,
    createBars,
    // getDateBasedOnFilter
} from '../utils.js'
import {
    compareItemNames,
    compareStock,
    compareDates,
    getInitParamsForInventorySorter,
    searchInventory,
    getInventoryUsingId,
    createUpdateInventoryForm
} from './inventory-table.js'
import {
    getCountsAndLabelsForInventoryChart,
    getChartParams,
    createInventoryChart,
    getTrendsParams,
    getInventoryItem,
} from './inventory-chart.js'
import {
    sortInventoryData,
    countCurrentStocksAndExpiredItems,
    createInventoryBar
} from './inventory-stock.js'

const sortedInventory = JSON.parse(document.getElementById('sorted-inventory').textContent)
const countedInventory = JSON.parse(document.getElementById('counted-inventory').textContent)
const inventoryData = JSON.parse(document.getElementById('inventory-data').textContent)
const token = document.getElementsByName('csrfmiddlewaretoken')[0].value

await main()

async function main() {
    createLogicTrendsBar()
    createLogicInventoryChart()
    createLogicInventoryBar()

    listenToInventoryCategoryBtns()
    listenToInventorySortSelector()
    listenInventorySortDirectionBtn()
    listenToSearchBtn()
    listenToAddInventoryBtn()
    listenToInventorySearchContainer()
    listenToInventoryButtons()
    listenToInventoryDeleteButtons()

    listenChartCategoryBtns()
    listenChartFilterBtns()

    listenInventoryTrendsCategoryBtns()
    listenInventoryTrendsFilterBtns()

    // 
    listen_all_number_input()
}

function listen_all_number_input() {
    const inputs = document.querySelectorAll('input[type="number"]')
    
    if (inputs.length <= 0) {
        return
    }

    for (const input of inputs) {
        input.addEventListener('input', () => {
            const inputted_number = parseFloat(input.value)

            if (inputted_number < 0) {
                input.value = 0
            }

        })
    }
}

function listenToInventoryDeleteButtons() {
    const inventoryDeleteBtns = document.querySelectorAll('.js-inventory-delete-btn')
    const deleteInventoryModal = document.getElementById('deleteInventoryModal')
    for (const deleteBtn of inventoryDeleteBtns) {
        deleteBtn.addEventListener('click', () => {
            const inventoryId = parseInt(deleteBtn.getAttribute('data-id'))
            const item = getInventoryUsingId(Object.values(sortedInventory), inventoryId)
            createDeleteInventoryForm(item, token)
            openModal(deleteInventoryModal)
            const cancelDeleteInventoryBtns = document.querySelectorAll('.js-close-delete-btn')
            for (const btn of cancelDeleteInventoryBtns) {
                closeModal(deleteInventoryModal, btn)
            }
        })
    }
}

function createDeleteInventoryForm(item, token) {
    const url = `/staff/inventory/delete/${item.id}/`
    const deleteInventoryForm = document.querySelector('#deleteInventoryModal .modal-content .form-body')
    let html = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${token}" />
        <div>Are you sure you want to delete "${item.item_name}"?</div>
        <div class="form-buttons">
            <button type="submit" class="add-btn">Delete</button>
            <button type="button" class="cancel-btn js-close-delete-btn">Cancel</button>
        </div>
    `
    deleteInventoryForm.innerHTML = html
    deleteInventoryForm.setAttribute('action', url)
}


function listenToInventoryButtons() {
    const inventoryBtns = document.querySelectorAll('.js-inventory-btn')
    const updateInventoryModal = document.getElementById('updatedInventoryModal')
    for (const inventoryBtn of inventoryBtns) {
        inventoryBtn.addEventListener('click', () => {
            const inventoryId = parseInt(inventoryBtn.getAttribute('data-id'))
            const item = getInventoryUsingId(Object.values(sortedInventory), inventoryId)
            createUpdateInventoryForm(item, token)
            openModal(updateInventoryModal)
            listen_all_number_input()
            const cancelInventoryBtns = document.querySelectorAll('.js-close-update-inventory-btn')
            for (const cancelInventoryBtn of cancelInventoryBtns) {
                closeModal(updateInventoryModal, cancelInventoryBtn)
            }
        })
    }
}

function createLogicInventoryBar() {
    if (inventoryData) {
        const categorizedData = sortInventoryData(inventoryData)
        const categorizedCounts = countCurrentStocksAndExpiredItems(categorizedData)
        createInventoryBar(categorizedCounts, createChart)
    }
}

function createLogicInventoryTable() {
    if (sortedInventory) {
        const {
            filter,
            inventorySort,
            sortDirection
        } = getInitParamsForInventorySorter(getActiveFilter)
        const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)
        updateInventoryTable(inventory)
        listenToInventoryButtons()
        listenToInventoryDeleteButtons()
    }
}

function createLogicInventoryChart() {
    if (countedInventory) {
        const {
            category,
            filter
        } = getChartParams(getActiveFilter)

        const data = countedInventory[category][filter]
        const {
            labels,
            counts
        } = getCountsAndLabelsForInventoryChart(data)
        createInventoryChart(labels, counts, category, createChart)
    }
}

function createLogicTrendsBar() {
    if (inventoryData) {
        const {
            trendCategory,
            trendFilter
        } = getTrendsParams(getActiveFilter)
        createTrendsBarCanvas(trendCategory, trendFilter)
        selectEachTrendsCanvasThenCreateTrendsBar(trendCategory, trendFilter)
    }
}

function selectEachTrendsCanvasThenCreateTrendsBar(trendCategory, trendFilter) {
    let maxCount = 0
    for (const inventory of Object.values(inventoryData)) {
        const trendsCategories = ['Medicine', 'Supply']
        for (const category of trendsCategories) {
            const filteredInventoryData = countedInventory[category][trendFilter]
            const inventoryItem = getInventoryItem(inventory.id, filteredInventoryData)
            let quantity = inventoryItem ? inventoryItem.total_quantity : 0
            maxCount += quantity
        }
    }

    for (const inventory of Object.values(inventoryData)) {
        if (inventory.category == trendCategory) {
            const trendCanvas = document.getElementById(`trends-bar-${inventory.id}`)
            const filteredInventoryData = countedInventory[trendCategory][trendFilter]
            const inventoryItem = getInventoryItem(inventory.id, filteredInventoryData)
            let quantity = inventoryItem ? inventoryItem.total_quantity : 0
            createBars(trendCanvas, maxCount, quantity)
        }
    }
}

function createTrendsBarCanvas(trendCategory, trendFilter) {
    const trendsBarSpace = document.querySelector('.bar-space')
    let html = ''

    for (const item of Object.values(inventoryData)) {
        if (item.category == trendCategory) {
            const filteredInventoryData = countedInventory[trendCategory][trendFilter]
            const inventoryItem = getInventoryItem(item.id, filteredInventoryData)
            let quantity = inventoryItem ? inventoryItem.total_quantity : 0
            html += `
                <div >
                    <div class="barsTop">
                        <h5>${item.item_name}</h5>
                        <h4>${quantity}</h4>
                    </div>
                    <div class="bars">
                        <canvas id="trends-bar-${item.id}"></canvas>
                    </div>
                </div>
            `

        }
        trendsBarSpace.innerHTML = html
    }
}

function listenInventoryTrendsCategoryBtns() {
    const trendsCategoryBtns = document.querySelectorAll('.js-seasonal-bar-category')
    for (const btn of trendsCategoryBtns) {
        btn.addEventListener('click', () => {
            const trendsClass = 'js-seasonal-bar-category-active'
            for (const btn of trendsCategoryBtns) {
                btn.classList.remove(trendsClass)
                btn.classList.remove('bottom-cat-btn-active')
            }
            btn.classList.add(trendsClass)
            btn.classList.add('bottom-cat-btn-active')
            createLogicTrendsBar()
        })
    }
}

function listenInventoryTrendsFilterBtns() {
    const trendFilterBtns = document.querySelectorAll('.js-seasonal-bar-filter')
    for (const btn of trendFilterBtns) {
        btn.addEventListener('click', () => {
            const filterClass = 'js-seasonal-bar-filter-active'
            for (const btn of trendFilterBtns) {
                btn.classList.remove(filterClass)
                btn.classList.remove('bar-btn-active')
            }
            btn.classList.add(filterClass)
            btn.classList.add('bar-btn-active')
            createLogicTrendsBar()
        })
    }
}

function listenChartCategoryBtns() {
    const chartCategoryBtns = document.querySelectorAll('.js-seasonal-category-btn')
    for (const btn of chartCategoryBtns) {
        btn.addEventListener('click', () => {
            for (const btn of chartCategoryBtns) {
                btn.classList.remove('js-seasonal-category-btn-active')
                btn.classList.remove('bottom-cat-btn-active')
            }
            btn.classList.add('js-seasonal-category-btn-active')
            btn.classList.add('bottom-cat-btn-active')
            createLogicInventoryChart()
            return
        })
    }
}

function listenChartFilterBtns() {
    const chartFilterBtns = document.querySelectorAll('.js-seasonal-filter')

    for (const btn of chartFilterBtns) {
        btn.addEventListener('click', () => {
            for (const btn of chartFilterBtns) {
                btn.classList.remove('js-seasonal-filter-active')
                btn.classList.remove('active-cat')
            }
            btn.classList.add('js-seasonal-filter-active')
            btn.classList.add('active-cat')
            createLogicInventoryChart()
            return

        })
    }

}

function listenToInventoryCategoryBtns() {
    const inventoryCategoryBtns = document.querySelectorAll('.js-inventory-category')
    for (const btn of inventoryCategoryBtns) {
        btn.addEventListener('click', () => {
            const filterClassName = 'js-inventory-category-active'
            const sorterName = 'data-sorter'

            for (const btn of inventoryCategoryBtns) {
                btn.classList.remove(filterClassName)
                btn.classList.remove('inventory_cat-active')
            }
            btn.classList.add(filterClassName)
            btn.classList.add('inventory_cat-active')
            createLogicInventoryTable()
        })
    }
}

function listenToInventorySortSelector() {
    const inventorySortSelector = document.querySelector('.js-inventory-sort-select')
    inventorySortSelector.addEventListener('change', () => {
        createLogicInventoryTable()
    })

}

function listenInventorySortDirectionBtn() {
    const inventorySortDirectionBtn = document.querySelector('.js-inventory-direction')
    inventorySortDirectionBtn.addEventListener('click', () => {
        const inventorySortDirection = getActiveFilter('js-inventory-direction', 'data-sort')
        if (inventorySortDirection == 'desc') {
            inventorySortDirectionBtn.setAttribute('data-sort', 'asc')
            // inventorySortDirectionBtn.innerHTML = 'Up'
        } else if (inventorySortDirection == 'asc') {
            inventorySortDirectionBtn.setAttribute('data-sort', 'desc')
            // inventorySortDirectionBtn.innerHTML = 'Down'
        }
        const {
            filter,
            inventorySort,
            sortDirection
        } = getInitParamsForInventorySorter(getActiveFilter)
        const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)
        createLogicInventoryTable()
    })
}

function getSortedInventoryData(filter, inventorySort, sortDirection) {
    let localInventory = sortedInventory
    let updatedData = []

    if (filter != 0) {
        for (const data of localInventory) {
            if (data.sorter == filter) {
                updatedData.push(data)
            }
        }
    } else {
        updatedData = localInventory
    }

    if (inventorySort == 'name') {
        updatedData = updatedData.sort((a, b) => compareItemNames(a, b, sortDirection))
    }
    if (inventorySort == 'stock') {
        updatedData = updatedData.sort((a, b) => compareStock(a, b, sortDirection))
    }
    if (inventorySort == 'date') {
        updatedData = updatedData.sort((a, b) => compareDates(a, b, sortDirection))
    }
    return updatedData
}

function updateInventoryTable(inventory) {
    const inventoryBody = document.getElementById('inventory-body')

    let html = ''
    if (inventory.length > 0) {
        for (const data of inventory) {
            html += `
                <tr>
                    <td class="table-data item-column">${data.item_name}</td>
                    <td class="table-data cat-column">${data.category}</td>
                    <td class="table-data total-column">${ data.total_quantity }</td>
                    <td class="table-data exp-column">${ data.expiration_date }</td>
                    <td class="table-data js-inventory-btn btn view-column" data-id="${data.id}">View</td>
                    <td class="table-data js-inventory-delete-btn btn delete-column" data-id="${data.id}"><span class="material-symbols-outlined delete-btn">
                                        delete
                                        </span></td>
                </tr>

            `
        }
    } else {
        html += `
            <tr>
                <td class="table-data" colspan="4">No inventory item found.</td>

            </tr>
        `
    }


    inventoryBody.innerHTML = html
}

function listenToSearchBtn() {
    const inventorySearchBtn = document.querySelector('.js-inventory-search-btn')

    inventorySearchBtn.addEventListener('click', () => {
        const {
            filter,
            inventorySort,
            sortDirection
        } = getInitParamsForInventorySorter(getActiveFilter)
        const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)
        const filteredInventory = searchInventory(inventory)
        updateInventoryTable(filteredInventory)
        listenToInventoryButtons()
        listenToInventoryDeleteButtons()
        // createLogicInventoryTable()
    })
}

function listenToAddInventoryBtn() {
    const addInventoryBtn = document.querySelector('.js-add-inventory-btn')
    const addInventoryModal = document.querySelector('.js-add-inventory-modal')
    const cancelInventoryBtns = document.querySelectorAll('.js-close-inventory-btn')
    addInventoryBtn.addEventListener('click', () => {
        openModal(addInventoryModal)
        listen_all_number_input()
        for (const cancelInventoryBtn of cancelInventoryBtns) {
            closeModal(addInventoryModal, cancelInventoryBtn)
        }

    })
}

function listenToInventorySearchContainer() {
    const inventorySearchContainer = document.querySelector('.js-inventory-search-container')
    inventorySearchContainer.addEventListener('mouseenter', () => {
        document.addEventListener('keypress', handleKeyPressOnInventorySearchContainer)
    })
    inventorySearchContainer.addEventListener('mouseleave', () => {
        document.removeEventListener('keypress', handleKeyPressOnInventorySearchContainer)
    })
}

function handleKeyPressOnInventorySearchContainer(event) {
    if (event.key === 'Enter') {
        const {
            filter,
            inventorySort,
            sortDirection
        } = getInitParamsForInventorySorter(getActiveFilter)
        const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)
        const filteredInventory = searchInventory(inventory)
        createLogicInventoryTable()
    }
}
