export function createRequestBarChart(labels, counts, createChart) {
    const canvas = document.getElementById('requestBar')
    const ctx = canvas.getContext('2d')
    const chartType = 'bar'
    const chartData = {
        labels: labels,
        datasets: [{
            data: counts,
            backgroundColor: [
              'rgba(255, 99, 132, 0.2)',
              'rgba(255, 159, 64, 0.2)',
              'rgba(255, 205, 86, 0.2)',
              'rgba(75, 192, 192, 0.2)',
              'rgba(54, 162, 235, 0.2)',
              'rgba(153, 102, 255, 0.2)',
              'rgba(201, 203, 207, 0.2)'
            ],
            borderColor: [
              'rgb(255, 99, 132)',
              'rgb(255, 159, 64)',
              'rgb(255, 205, 86)',
              'rgb(75, 192, 192)',
              'rgb(54, 162, 235)',
              'rgb(153, 102, 255)',
              'rgb(201, 203, 207)'
            ],
            borderWidth: 1
          }]
    }
    const chartOptions = {
        plugins: {
            legend: {
                display: false,
                labels: {
                    display: false,
                    // font: {
                    //     family: 'Poppins', // Your custom font family
                    //     size: 14, // Font size
                    //     weight: 'normal', // Font weight
                    //     style: 'normal' // Font style
                    // }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false // This removes the grid lines on the x-axis
                },
                ticks: {
                    font: {
                        family: 'Arial', // Web-safe font
                        size: 10,
                        weight: 'bold',
                        style: 'normal'
                    }
                }
            },
            y: {
                beginAtZero: true, // Ensure y-axis starts from 0
                display: false
            }
        }
    }
    const scrollPosition = window.scrollY || document.documentElement.scrollTop;
    createChart(ctx, chartType, chartData, chartOptions)
    window.scrollTo(0, scrollPosition);
}

export function getCountsAndLabelForRequestBar(data) {
    let counts = []
    let labels = []

    for (const item of data) {
        for (const [key, value] of Object.entries(item)) {
            labels.push(key)
            counts.push(value)
        }
    }

    return {
        counts,
        labels
    }
}
