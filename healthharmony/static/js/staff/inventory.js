import {
    getActiveFilter,
    openModal,
    closeModal,
    createChart
} from '/static/js/utils.js'
import {
    compareItemNames,
    compareStock,
    compareDates,
    getInitParamsForInventorySorter,
    searchInventory
} from '/static/js/staff/inventory-table.js'
import {
    getCountsAndLabelsForInventoryChart,
    getChartParams
} from '/static/js/staff/inventory-chart.js'

const sortedInventory = JSON.parse(document.getElementById('sorted-inventory').textContent)
const countedInventory = JSON.parse(document.getElementById('counted-inventory').textContent)
const inventoryData = JSON.parse(document.getElementById('inventory-data').textContent)

main()

function main() {
    console.log(countedInventory)
    listenToInventoryCategoryBtns()
    listenToInventorySortSelector()
    listenInventorySortDirectionBtn()
    listenToSearchBtn()
    listenToAddInventoryBtn()
    listenToInventorySearchContainer()
    listenChartCategoryBtns()
    listenChartFilterBtns()

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

function createInventoryChart(labels, counts, categoryName, createChart) {
    const canvas = document.getElementById('js-seasonal-canvas')
    const ctx = canvas.getContext('2d')

    const chartType = 'line'
    const chartData = {
        labels: labels,
        datasets: [{
            label: categoryName,
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
        plugins: {
            legend: {
                labels: {
                    font: {
                        family: 'Poppins', // Your custom font family
                        size: 14, // Font size
                        weight: 'normal', // Font weight
                        style: 'normal' // Font style
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false // This removes the grid lines on the x-axis
                },
                ticks: {
                    font: {
                        family: 'Arial', // Web-safe font
                        size: 10,
                        weight: 'bold',
                        style: 'normal'
                    }
                }
            },
            y: {
                beginAtZero: true, // Ensure y-axis starts from 0
                display: false
            }
        }
    }

    createChart(ctx, chartType, chartData, chartOptions)
}

function listenChartCategoryBtns() {
    const chartCategoryBtns = document.querySelectorAll('.js-seasonal-category-btn')
    for (const btn of chartCategoryBtns) {
        btn.addEventListener('click', () => {
            for (const btn of chartCategoryBtns) {
                btn.classList.remove('js-seasonal-category-btn-active')
            }
            btn.classList.add('js-seasonal-category-btn-active')
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

        })
    }
}

function listenChartFilterBtns() {
    const chartFilterBtns = document.querySelectorAll('.js-seasonal-filter')

    for (const btn of chartFilterBtns) {
        btn.addEventListener('click', () => {
            for (const btn of chartFilterBtns) {
                btn.classList.remove('js-seasonal-filter-active')
            }
            btn.classList.add('js-seasonal-filter-active')
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
            }
            btn.classList.add(filterClassName)
            const {
                filter,
                inventorySort,
                sortDirection
            } = getInitParamsForInventorySorter(getActiveFilter)
            const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)
            updateInventoryTable(inventory)
        })
    }
}

function listenToInventorySortSelector() {
    const inventorySortSelector = document.querySelector('.js-inventory-sort-select')
    inventorySortSelector.addEventListener('change', () => {
        const {
            filter,
            inventorySort,
            sortDirection
        } = getInitParamsForInventorySorter(getActiveFilter)
        const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)
        updateInventoryTable(inventory)
    })

}

function listenInventorySortDirectionBtn() {
    const inventorySortDirectionBtn = document.querySelector('.js-inventory-direction')
    inventorySortDirectionBtn.addEventListener('click', () => {
        const inventorySortDirection = getActiveFilter('js-inventory-direction', 'data-sort')
        if (inventorySortDirection == 'desc') {
            inventorySortDirectionBtn.setAttribute('data-sort', 'asc')
            inventorySortDirectionBtn.innerHTML = 'Up'
        } else if (inventorySortDirection == 'asc') {
            inventorySortDirectionBtn.setAttribute('data-sort', 'desc')
            inventorySortDirectionBtn.innerHTML = 'Down'
        }
        const {
            filter,
            inventorySort,
            sortDirection
        } = getInitParamsForInventorySorter(getActiveFilter)
        const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)
        updateInventoryTable(inventory)
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
                    <td class="table-data">${data.item_name}</td>
                    <td class="table-data">${data.category}</td>
                    <td class="table-data">${ data.total_quantity }</td>
                    <td class="table-data">${ data.expiration_date }</td>
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
    })
}

function listenToAddInventoryBtn() {
    const addInventoryBtn = document.querySelector('.js-add-inventory-btn')
    const addInventoryModal = document.querySelector('.js-add-inventory-modal')
    const cancelInventoryBtns = document.querySelectorAll('.js-close-inventory-btn')
    addInventoryBtn.addEventListener('click', () => {
        openModal(addInventoryModal)
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
        updateInventoryTable(filteredInventory)
    }
}
