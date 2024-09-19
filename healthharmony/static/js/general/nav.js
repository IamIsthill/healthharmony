try {
    handle_onclick_profile()

} catch (error) {
    console.error(error.message)
}


// When user clicks the profile
function handle_onclick_profile() {
    const profile_container = document.querySelector('.js_profile_info')

    profile_container.addEventListener('click', () => {
        const url = new URL(window.location.href)
        url.pathname = '/user_profile/'
        window.location.href = url
    })
}
