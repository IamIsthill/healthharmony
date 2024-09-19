try {
    handle_onclick_profile()

} catch (error) {
    console.error(error.message)
}


// When user clicks the profile
function handle_onclick_profile() {
    const profile_containers = document.querySelectorAll('.js_profile_info')

    for (const profile_container of profile_containers) {
        profile_container.addEventListener('click', () => {
            console.log('navigation bar was clicked')
        })
    }
}
