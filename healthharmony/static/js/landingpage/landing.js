const doctor_data = JSON.parse(document.getElementById('doctor_data').textContent)

console.log(doctor_data)

handle_making_readable_time()

// make time readable
function handle_making_readable_time() {
    const time_elements = document.querySelectorAll('.js_time')

    if (time_elements.length == 0) {
        return
    }

    for (const time_element of time_elements) {
        if (time_element.innerText != '') {
            const time = formatTime(time_element.innerText)
            time_element.innerText = time
        }
    }

}


// Time formatter
function formatTime(date) {
    let [hours, minutes] = date.split(':').map(Number); // Split and convert to numbers
    let ampm = hours >= 12 ? 'PM' : 'AM'; // Determine AM or PM
    hours = hours % 12 || 12; // Convert to 12-hour format and handle 0 as 12
    minutes = minutes < 10 ? '0' + minutes : minutes; // Add leading zero if needed
    return hours + ':' + minutes + ' ' + ampm;
}
