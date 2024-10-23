import {
    openModal,
    closeModal
} from '../utils.js'

const user_email = JSON.parse(document.getElementById('user_email').textContent)

main()

//Grouping the main logic
async function main() {
    let visitData = await fetchVisitData(user_email);
    visitData = visitData.visit_data;
    let treatmentData = await fetchTreatmentData(user_email);
    const treatmentDataLabels = Object.entries(treatmentData.labels)
    // treatmentData = (treatmentData.illness_count)


    updateVisitCanvas(visitData.year)
    createTreatmentBarsCanvas(treatmentData, 'week', treatmentDataLabels)
    updateTreatmentBars(treatmentData, 'week', treatmentDataLabels)

    // Date Filter for Visit Records
    handle_onclick_visit_filters(visitData)

    // Date Filter for treatments
    handle_onclick_treatment_filters(treatmentData, treatmentDataLabels)

    // request a medcert
    handle_onclick_request_medcert()

}
//======================================================

// Show modal when user requests a medcert
function handle_onclick_request_medcert() {
    const btn = document.querySelector('.js_request_medcert_btn')

    btn.addEventListener('click', () => {
        const modal = document.querySelector('.js_request_medcert_modal')
        const close_btns = document.querySelectorAll('.js_close_medcert_modal')

        openModal(modal)

        for (const close of close_btns) {
            closeModal(modal, close)
        }

    })
}

// User clicks the date filters for the visit history
function handle_onclick_visit_filters(visitData) {
    const visitFilterBtns = document.querySelectorAll(".visit-filter");
    visitFilterBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const text = btn.getAttribute("data-category").toLowerCase();
            updateVisitCanvas(visitData[text]);
        });
    });
}

// User clicks the filters for the recent treatments
function handle_onclick_treatment_filters(treatmentData, treatmentDataLabels) {
    const treatmentFilterBtns = document.querySelectorAll('.treatment-filter')
    treatmentFilterBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const text = btn.getAttribute('data-category').toLowerCase()
            updateTreatmentBars(treatmentData, text, treatmentDataLabels)
        })
    })

}

//Update the treatment bars
function updateTreatmentBars(data, filter, labels) {
    try {
        data = Object.entries(data[filter])

        let maxCount = 0

        for (const [key, value] of data) {
            maxCount += parseInt(value)
        }


        for (const [key, value] of data) {

            const treatment_name = (getTreatmentName(labels, key))
            const canvasId = `${key}-${treatment_name}`;
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.error(`Canvas with ID ${treatment_name}-${key} not found`);
                continue;
            }
            const ctx = canvas.getContext('2d')
            // Clear and reset the canvas dimensions
            canvas.width = 0
            canvas.height = 0
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;

            //background bar
            ctx.fillStyle = '#E4E7EC'
            ctx.fillRect(0, 0, parseInt(canvas.width), parseInt(canvas.height))

            //foreground bar
            ctx.fillStyle = '#FFDA80'
            let width = ((parseInt(canvas.width)) / maxCount) * (parseInt(value))
            ctx.fillRect(0, 0, width, parseInt(canvas.height))
        }


    } catch (error) {
        console.error(error.message)
    }

}
//======================================================

// Return treatment name using treatment id
function getTreatmentName(labels, id) {
    for (const [key, value] of labels) {
        if (key == id) {
            return value
        }
    }
}
//======================================================

// Create the canvas for the bars based on treatment data
function createTreatmentBarsCanvas(data, filter, labels) {
    try {
        data = Object.entries(data[filter])
        const treatmentBarSpace = document.getElementById('treatment-bar-space')
        let mainHTML = ''
        for (const [key, value] of data) {
            let treatment_name = (getTreatmentName(labels, key))
            let html = `
      <div>
        <h6> ${treatment_name} </h6>
        <div>
          <canvas id="${key}-${treatment_name}"></canvas>
        </div>
      </div>
      `
            mainHTML += html
        }
        treatmentBarSpace.innerHTML = mainHTML

    } catch (error) {
        const treatmentBarSpace = document.getElementById('treatment-bar-space')
        treatmentBarSpace.parentElement.style.display = 'none'
    }
}
//======================================================

// get visit data using email
async function fetchTreatmentData(email) {
    try {
        let baseUrl = window.location.origin;
        let url = new URL(`${baseUrl}/api/patient/treatment-data/`);

        if (email) {
            url.searchParams.append("email", email);
        }
        const options = {
            method: "GET",
        };

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    } catch (err) {
        console.log(`Failed to fetch session: ${err.message}`);
        return null;
    }
}
//======================================================

// get visit data using email
async function fetchVisitData(email) {
    try {
        let baseUrl = window.location.origin;
        let url = new URL(`${baseUrl}/api/patient/visit-data/`);

        if (email) {
            url.searchParams.append("email", email);
        }
        const options = {
            method: "GET",
        };

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    } catch (err) {
        console.log(`Failed to fetch session: ${err.message}`);
        return null;
    }
}
//======================================================

// Function for updating the visit canvas
function updateVisitCanvas(data) {
    const visitCanvas = document.getElementById("visitCanvas");
    const ctx = visitCanvas.getContext("2d");

    data = Object.entries(data)
    let xLabels = [];
    let dataPoints = [];
    for (const [key, value] of data) {
        xLabels.push(key);
        dataPoints.push(value);
    };


    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy(); // Destroy if it exists
    }

    const chart_type = "line"

    const chart_data = {
        labels: xLabels,
        datasets: [{
            label: "Visit Count",
            data: dataPoints,
            backgroundColor: "rgba(204, 144, 0, 1)",
            borderColor: "rgba(255, 99, 132, 1)",
            borderWidth: 1,
        }, ],
    }

    const chart_options = {
        scales: {
            x: {
                stacked: true,
                grid: {
                    display: false,
                },
            },
            y: {
                beginAtZero: false,
                stacked: true,
                min: 0,
                ticks: {
                    display: false,
                },
                grid: {
                    display: false,
                },
            },
        },
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
        },
    }

    try {
        window.myChart = new Chart(ctx, {
            type: chart_type,
            data: chart_data,
            options: chart_options,
        });

    } catch (error) {
        console.error(error.message)
    }

}
//======================================================
