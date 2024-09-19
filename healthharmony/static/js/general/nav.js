try {
    handle_onclick_profile()
    handle_hover_profile()

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

// WHen user hovers on the profile
// function handle_hover_profile() {
//     const profile_container = document.querySelector('.js_profile_info')

//     profile_container.addEventListener('mouseover', (event) => {
//         const existing_element = document.querySelectorAll('.js_profile_dropdown')
//         console.log(profile_container.getBoundingClientRect())

//         if (existing_element.length > 0) {
//             return
//         }
//         const coords = profile_container.getBoundingClientRect()
//         const div_element = document.createElement('div')

//         div_element.classList.add('js_profile_dropdown')

//         div_element.style.top = `${coords.y-5}px`
//         div_element.style.left = `${coords.x+5}px`
//         div_element.style.zIndex = '1000'
//         div_element.style.background = 'red'

//         div_element.style.position = 'relative'
//         const content = `
//             <a href="#">Profile Settings</href>
//             <a href="#">Reset Password</href>
//             <a href="#">Logout</href>
//         `
//         div_element.innerHTML = content


//         document.body.appendChild(div_element)

//     })

// }
