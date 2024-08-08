export function getCategoryFilter() {
    const activeCategoryFilter = document.querySelector('.active-category-filter')
    const filter = activeCategoryFilter.getAttribute('data-category-data')
    return filter
}

export function getCategoryName(id, filter, categoryData) {
    const categoryName = categoryData[filter][id]
    return String(Object.keys(categoryName))
}

export function getSelectedCategoryId() {
    const categorySelector = document.getElementById('categories')
    const id = parseInt(categorySelector.value)
    return id
}

export function getCategoryNames(filter, categoryData) {
    let categoryNames = {}
    for (const [id, category] of Object.entries(categoryData[filter])) {
        for (const name of Object.keys(category)) {
            categoryNames[id] = name
        }
    }
    return categoryNames
}
