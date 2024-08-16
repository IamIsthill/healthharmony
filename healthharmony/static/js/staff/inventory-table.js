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

    if (isNaN(dateA.getTime()) || isNaN(dateB.getTime())) {
        return 0
    }

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

export function searchInventory(inventory) {
    const inventorySearchContainer = document.querySelector('.js-inventory-search-container')
    let searchText = inventorySearchContainer.value.toLowerCase()
    const filteredInventory = inventory.filter((data) => {
        if (
            data.item_name.toLowerCase().includes(searchText) ||
            data.category.toLowerCase().includes(searchText) ||
            data.expiration_date.toLowerCase().includes(searchText) ||
            String(data.total_quantity).includes(searchText)

        ) {
            return data
        }
    })
    inventorySearchContainer.value = ''
    return filteredInventory
}


export function getInventoryUsingId(sortedInventory, id) {
    const mid = Math.round((sortedInventory.length) / 2)
    const firstHalfArr = sortedInventory.slice(0, mid)
    const secondHalfArr = sortedInventory.slice(mid)

    for (const item of firstHalfArr) {
        if (item.id === id) {
            return item
        }
    }
    if (secondHalfArr.length > 0) {
        return getInventoryUsingId(secondHalfArr, id);
    } else {
        return null; // Or return undefined
    }
}

export function createUpdateInventoryForm(item, token) {
    const updateInventoryForm = document.querySelector('#updatedInventoryModal .modal-content .form-body')
    let html = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${token}" />
        <div class="form-top">
            <label for="item_name">Item Name</label>
            <input type="text" placeholder="name.." name="item_name" value="${item.item_name}" required />
        </div>
        <div class="form-middle">
            <div class="form-group">
                <label for="item_no">Item Number</label>
                <input type="number" placeholder="#" name="item_no" value="${item.item_no}" required />
            </div>
            <div class="form-group">
                <label for="unit">Unit Type</label>
                <input type="text" placeholder="unit type.." name="unit" value="${item.unit}" required />
            </div>
        </div>
        <div class="form-bottom">
            <div class="form-group">
                <label for="category">Category</label>
                <select name="category" value="${item.category}"required>
                    <option value="Medicine">Medicine</option>
                    <option value="Supply">Supply</option>
                </select>
            </div>
            <div class="form-group">
                <label for="expiration_date">Expiration Date</label>
                <input type="date" name="expiration_date" value="${item.expiration_date}"/>
            </div>
            <div class="form-group">
                <label for="quantity">Quantity</label>
                <input type="number" name="quantity" value="${item.total_quantity}" />
            </div>
        </div>
        <div class="form-last">
            <label for="description">Item Description</label>
            <input type="search" placeholder="description.." name="description" value="${item.description}" />
        </div>
        <div class="form-buttons">
            <button type="submit" class="add-btn">Add</button>
            <button type="button" class="cancel-btn js-close-update-inventory-btn">Cancel</button>
        </div>
    `
    updateInventoryForm.innerHTML = html
}
