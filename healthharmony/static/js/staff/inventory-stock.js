export function sortInventoryData(inventoryData) {
    let categorizedData = {}
    for (const inventory of Object.values(inventoryData)) {
        const category = inventory.category;

        if (!categorizedData[category]) {
            categorizedData[category] = [];
        }

        categorizedData[category].push(inventory);
    }
    return categorizedData
}

export function countCurrentStocksAndExpiredItems(categorizedData) {
    let counts = {}
    let totalCounts = 0

    for (const item of Object.values(categorizedData)) {
        for (const data of Object.values(item)) {
            totalCounts += data.quantity
        }
    }

    for (const category of Object.keys(categorizedData)) {
        let goodStocks = 0
        let badStock = 0
        if (!counts[category]) {
            counts[category] = []
        }

        for (const item of Object.values(categorizedData[category])) {
            const expiratioDate = new Date(item.expiration_date)
            const now = new Date()
            if (expiratioDate < now) {
                badStock += item.quantity
            } else {
                goodStocks += item.quantity
            }

        }

        const total = totalCounts - (goodStocks + badStock)

        counts[category].push([goodStocks, badStock, total])
    }

    return counts
}

export function createInventoryBar(categorizedCounts, createChart) {
    const inventoryBarChartCanvas = document.getElementById('inventory-chart')
    const ctx = inventoryBarChartCanvas.getContext('2d')
    const chartType = 'bar'
    const chartData = {
        labels: ['Current Stocks', 'Expired Items'],
        datasets: [{
            label: 'Medicine',
            data: categorizedCounts['Medicine'][0],
            borderWidth: 1,
            borderColor: '#36A2EB',
            backgroundColor: '#9BD0F5',
            fill: false,
        }, {
            label: 'Supply',
            data: categorizedCounts['Supply'][0],
            borderColor: '#FF6384',
            backgroundColor: '#FFB1C1',
        }]
    };

    const chartOptions = {
        plugins: [{
            legend: {
                labels: {
                    font: {
                        family: 'Poppins', // Your custom font family
                        size: 14, // Font size
                        weight: 'normal', // Font weight
                        style: 'normal' // Font style
                    }
                }
            }
        }],
        scales: {
            x: {
                stacked: true,
            },
            y: {
                stacked: true,
            }
        }
    };

    createChart(ctx, chartType, chartData, chartOptions)
}
