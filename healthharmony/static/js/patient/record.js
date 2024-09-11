
main()

function main() {
    getPatientIdFromUrl()
    changeUrlBasedOnIdFromUrl()
}

function getPatientIdFromUrl() {
    const url = window.location.pathname
    const splitUrl = url.split("/")
    const id = splitUrl[splitUrl.length - 2]
    return id
}

function changeUrlBasedOnIdFromUrl() {
    const links = document.querySelectorAll('.js-nav-links')
    for (const link of links) {
        const containedLink = link.getAttribute('href')
        let arrayedLink = containedLink.split("/")
        if (arrayedLink.length > 3){
            const patientId = getPatientIdFromUrl()
            arrayedLink[arrayedLink.length - 2] = patientId
            let stringLink = arrayedLink.toString()
            stringLink = stringLink.replace(/,/g, "/")
            link.setAttribute('href', stringLink)
        }

    }
}
