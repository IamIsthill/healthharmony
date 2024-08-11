import {
    getActiveFilter
} from '/static/js/utils.js'
import {
    compareItemNames,
    compareStock,
    compareDates,
    getInitParamsForInventorySorter
} from '/static/js/staff/inventory-table.js'

const sortedInventory = JSON.parse(document.getElementById('sorted-inventory').textContent)

main()

function main() {
    listenToInventoryCategoryBtns()
    listenToInventorySortSelector()
    listenInventorySortDirectionBtn()

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
            updateInventoryTable()
        })
    }
}

function listenToInventorySortSelector() {
    const inventorySortSelector = document.querySelector('.js-inventory-sort-select')
    inventorySortSelector.addEventListener('change', () => {
        updateInventoryTable()
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
        updateInventoryTable()
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

function updateInventoryTable() {
    const inventoryBody = document.getElementById('inventory-body')
    const {
        filter,
        inventorySort,
        sortDirection
    } = getInitParamsForInventorySorter(getActiveFilter)
    const inventory = getSortedInventoryData(filter, inventorySort, sortDirection)

    let html = ''
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

    inventoryBody.innerHTML = html
}
