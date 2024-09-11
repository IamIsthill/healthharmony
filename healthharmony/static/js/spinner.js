export async function setSpinner(container, spinner, link) {
    container.style.display = 'none'
    spinner.style.display = 'block'
    try {
        let baseUrl = window.location.href;
        let url = new URL(`${baseUrl}`);
        const options = {
            method: "GET",
        };
        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        setTimeout(() => {
            spinner.style.display = "none";
            container.style.display = "block";
        }, 400);
    } catch (err) {
        console.log(`System faced some error: ${err.message}`);
    }
}
