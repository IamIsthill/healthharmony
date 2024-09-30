handle_onclick_pagination_links()


// Prevent default of the links and add them instead to the url params
function handle_onclick_pagination_links() {
    const links = document.querySelectorAll('.js-links')

    for (const link of links) {
        link.addEventListener('click', (event) => {
            event.preventDefault()

            const url_params = link.getAttribute('href')
            const {
                key,
                value
            } = get_key_value_from_href(url_params)
            const current_url = new URL(window.location.href)
            if (current_url.searchParams.size >= 1) {
                if (current_url.searchParams.has(key)) {
                    current_url.searchParams.delete(key)
                }
            }
            current_url.searchParams.append(key, value)
            window.location.href = current_url
        })
    }
}

// Trim url to get key value pair
function get_key_value_from_href(url_params) {
    // Remove the question mark then reassign value
    let params = url_params.split('?')
    params = params[1]

    // separate by the equal sign
    params = params.split('=')

    const key = params[0]
    const value = params[1]

    return {
        'key': key,
        'value': value
    }
}
