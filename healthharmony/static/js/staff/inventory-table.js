export function compareItemNames(a, b, direction) {
    const itemA = a.item_name.toLowerCase()
    const itemB = b.item_name.toLowerCase()

    if (direction === 'asc') {
        if (itemA < itemB) {
            return -1
        }
        if (itemA > itemB) {
            return 1
        }
    } else {
        if (itemA < itemB) {
            return 1
        }
        if (itemA > itemB) {
            return -1
        }
    }
    return 0
}

export function compareStock(a, b, direction) {
    const stockA = a.total_quantity || 0
    const stockB = b.total_quantity || 0

    if (direction === 'asc') {
        return stockA - stockB
    } else {
        return stockB - stockA
    }
}

export function compareDates(a, b, direction) {
    const dateA = new Date(a.expiration_date)
    const dateB = new Date(b.expiration_date)

    if (direction === 'asc') {
        return dateA - dateB
    } else {
        return dateB - dateA
    }
}

export function getInitParamsForInventorySorter(getActiveFilter) {
    const filter = parseInt(getActiveFilter('js-inventory-category-active', 'data-sorter'))
    const inventorySort = document.querySelector('.js-inventory-sort-select').value
    const sortDirection = document.querySelector('.js-inventory-direction').getAttribute('data-sort')

    return {
        filter,
        inventorySort,
        sortDirection
    }
}
