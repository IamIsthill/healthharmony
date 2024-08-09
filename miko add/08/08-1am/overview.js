document.addEventListener('DOMContentLoaded', () => {
    let yearData = true
    let monthData = false
    let weekData = false
    let yearBarData = true
    let monthBarData = false
    let weekBarData = false
    let departmentYearBarData = true
    let departmentMonthBarData = false
    let departmentWeekBarData = false
    let patientYearData = true
    let patientMonthData = false
    let patientWeekData = false
    let departmentId = 1
    let categoryCases = JSON.parse(document.getElementById('category-cases').textContent)
    let categoryNames = JSON.parse(document.getElementById('category-cases').textContent)
    categoryNames = JSON.parse(categoryNames.categories)
    let departmentNames = JSON.parse(document.getElementById('department-names').textContent)
    let patientData = JSON.parse(document.getElementById('patient-cases').textContent)
    let categoryOpt = document.getElementById('categories')

    //Filters for each graphs

    let categoryDateFilterBtn = document.querySelectorAll('.categoryDateFilter')
    categoryDateFilterBtn.forEach((btn) => {
        btn.addEventListener('click', () => {
            let dateFilter = btn.getAttribute('data-category-data')
            if (dateFilter == 'past-12') {
                yearData = true
                monthData = false
                weekData = false
            } else if (dateFilter == 'past-30') {
                yearData = false
                monthData = true
                weekData = false
            } else if (dateFilter == 'past-7') {
                yearData = false
                monthData = false
                weekData = true
            }
            updateMorbidityChart(parseInt(categoryOpt.value))
        })
    })
    let patientDateFilterBtn = document.querySelectorAll('.patientDateFilter')
    patientDateFilterBtn.forEach((btn) => {
        btn.addEventListener('click', () => {
            let dateFilter = btn.getAttribute('data-patient-data')
            if (dateFilter == 'yearly') {
                patientYearData = true
                patientMonthData = false
                patientWeekData = false
            } else if (dateFilter == 'monthly') {
                patientYearData = false
                patientMonthData = true
                patientWeekData = false
            } else if (dateFilter == 'weekly') {
                patientYearData = false
                patientMonthData = false
                patientWeekData = true
            }
            updatePatientChart()
        })
    })

    let categoryBarDateFilterBtn = document.querySelectorAll('.categoryBarFilter')
    categoryBarDateFilterBtn.forEach((btn) => {
        btn.addEventListener('click', () => {
            let dateFilter = btn.getAttribute('data-category-data')
            if (dateFilter == 'yearly') {
                yearBarData = true
                monthBarData = false
                weekBarData = false
            } else if (dateFilter == 'monthly') {
                yearBarData = false
                monthBarData = true
                weekBarData = false
            } else if (dateFilter == 'weekly') {
                yearBarData = false
                monthBarData = false
                weekBarData = true
            }
            updateEachMorbidityBar()
        })
    })

    let departmentBarDateFilterBtn = document.querySelectorAll('.departmentBarFilter')
    departmentBarDateFilterBtn.forEach((btn) => {
        btn.addEventListener('click', () => {
            let dateFilter = btn.getAttribute('data-category-data')
            if (dateFilter == 'yearly') {
                yearBarData = true
                monthBarData = false
                weekBarData = false
            } else if (dateFilter == 'monthly') {
                yearBarData = false
                monthBarData = true
                weekBarData = false
            } else if (dateFilter == 'weekly') {
                yearBarData = false
                monthBarData = false
                weekBarData = true
            }
            console.log(dateFilter)

        })
    })

    // Function to update chart based on selected category
    function updateMorbidityChart(selectedOpt) {
        let dateFilter
        if (yearData == true) {
            dateFilter = 'yearly'
        } else if (monthData == true) {
            dateFilter = 'monthly'
        } else if (weekData == true) {
            dateFilter = 'weekly'
        }
        const ctx = document.getElementById('morbidityChart').getContext('2d')
        let title
        categoryNames.forEach(function(name) {
            if (name.id == selectedOpt) {
                title = name.category
            }
        })

        const perCategoryData = JSON.parse(categoryCases[dateFilter][selectedOpt])
        const categories = []
        const counts = []
        perCategoryData.forEach((data) => {
            categories.push(data[0])
            counts.push(data[1])
        })
        let existingChart = Chart.getChart(ctx)
        if (existingChart) {
            existingChart.destroy() // Destroy if it exists
        }

        // Create new chart instance
        window.myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: categories,
                datasets: [{
                    label: title,
                    data: counts,
                    borderWidth: 3,
                    indexAxis: 'x',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)', // Simplified background color for line chart
                    borderColor: 'rgba(255, 45, 26,0.5)', // Adding border color for better visualization
                    fill: false,
                    tension: 0.5
                }]
            },
            options: {
                plugins: {
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
        })
    }

    function updatePatientChart() {
        let dateFilter
        if (patientYearData == true) {
            dateFilter = 'yearly'
        } else if (patientMonthData == true) {
            dateFilter = 'monthly'
        } else if (patientWeekData == true) {
            dateFilter = 'weekly'
        }

        const ctx = document.getElementById('patientChart').getContext('2d')
        let title
        departmentNames.forEach(function(name) {
            if (name.id == departmentId) {
                title = name.department
            }
        })

        const perCategoryData = JSON.parse(patientData[dateFilter][departmentId])
        const categories = []
        const counts = []
        perCategoryData.forEach((data) => {
            categories.push(data[0])
            counts.push(data[1])
        })
        let existingChart = Chart.getChart(ctx)
        if (existingChart) {
            existingChart.destroy() // Destroy if it exists
        }

        // Create new chart instance
        window.myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: categories,
                datasets: [{
                    label: title,
                    data: counts,
                    borderWidth: 1,
                    indexAxis: 'x',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)', // Simplified background color for line chart
                    borderColor: 'rgba(75, 192, 192, 1)', // Adding border color for better visualization
                    fill: false,
                    tension: 0.5
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true // Ensure y-axis starts from 0
                    }
                }
            }
        })
    }


    // Initial setup on page load
    updateMorbidityChart(parseInt(categoryOpt.value))
    updatePatientChart()
    let departmentNamesBtn = document.querySelectorAll('.departmentNames')
    departmentNamesBtn.forEach((btn) => {
        btn.addEventListener('click', () => {
            let data = parseInt(btn.getAttribute('data-department-id'))
            departmentId = data
            updatePatientChart()
        })
    })

    //Dynamically create the canvas per category
    let morbidityBars = document.getElementById('morbidityBars')
    let htmlMorbidityBars = ''
    categoryNames.forEach(function(name) {
        let html = `
      <div>
        <h2>${name.category}</h2>
        <h2><span id="category-value-${name.id}"></></h2>
        <div class="bars">
          <canvas id="category-${name.id}"></canvas>
        </div>
      </div>
    `
        htmlMorbidityBars += html
    })
    morbidityBars.innerHTML = htmlMorbidityBars
    //==================================================================


    //Dynamically create the canvas per department
    let departmentBars = document.getElementById('departmentBars')
    let htmlDepartmentBars = ''
    departmentNames.forEach(function(name) {
        let html = `
      <div>
        <h4>${name.department}</h4>
        <h4><span id="department-value-${name.id}"></></h4>
        <div class="bars">
          <canvas id="department-${name.id}"></canvas>
        </div>
      </div>
    `
        htmlDepartmentBars += html
    })
    departmentBars.innerHTML = htmlDepartmentBars
    //==================================================================

    // function for preparing the data for the department morbidityBars
    function updateEachDepartmentBar() {
        let dateFilter
        if (departmentYearBarData == true) {
            dateFilter = 'yearly_count'
        } else if (departmentMonthBarData == true) {
            dateFilter = 'monthly_count'
        } else if (departmentWeekBarData == true) {
            dateFilter = 'weekly_count'
        }

        const perCategoryData = patientData[dateFilter]

        const categories = []
        const counts = []
        Object.entries(perCategoryData).forEach(([key, value]) => {
            categories.push(key)
            counts.push(value)
        })

        let maxCount = 0
        counts.forEach((count) => {
            maxCount += count
        })

        Object.entries(perCategoryData).forEach(([key, value]) => {
            let eachBar = document.getElementById(`department-${key}`)
            let title
            categoryNames.forEach(function(name) {
                if (name.id == parseInt(key)) {
                    title = name.category
                }
                createDepartmentBars(eachBar, maxCount, value)
            })
            document.getElementById(`department-value-${key}`).innerText = value;

        })
    }
    updateEachDepartmentBar()
    //==================================================================

    //Function for creating the actual department bars
    function createDepartmentBars(eachBar, maxCount, value) {
        let canvas = eachBar;
        let ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        canvas.width = 0
        canvas.height = 0
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;

        //background bar
        ctx.fillStyle = '#E4E7EC'
        ctx.fillRect(0, 0, parseInt(canvas.width), parseInt(canvas.height))

        //foreground bar
        ctx.fillStyle = '#FFDA80'
        let width = (parseInt(canvas.width)) / maxCount * (parseInt(value))
        ctx.fillRect(0, 0, width, parseInt(canvas.height))
    }
    //==================================================================


    function updateEachMorbidityBar() {
        let dateFilter
        if (yearBarData == true) {
            dateFilter = 'yearly_count'
        } else if (monthBarData == true) {
            dateFilter = 'monthly_count'
        } else if (weekBarData == true) {
            dateFilter = 'weekly_count'
        }

        const perCategoryData = categoryCases[dateFilter]

        const categories = []
        const counts = []
        Object.entries(perCategoryData).forEach(([key, value]) => {
            categories.push(key)
            counts.push(value)
        })

        let maxCount = 0
        counts.forEach((count) => {
            maxCount += count
        })

        Object.entries(perCategoryData).forEach(([key, value]) => {
            let eachBar = document.getElementById(`category-${key}`)
            let title
            categoryNames.forEach(function(name) {
                if (name.id == parseInt(key)) {
                    title = name.category
                }
            })
            document.getElementById(`category-value-${key}`).innerText = value;
            createMorbidityBars(eachBar, maxCount, value)
        })
    }

    function createMorbidityBars(eachBar, maxCount, value) {
        let canvas = eachBar;
        let ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        canvas.width = 0
        canvas.height = 0
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;

        //background bar
        ctx.fillStyle = '#E4E7EC'
        ctx.fillRect(0, 0, parseInt(canvas.width), parseInt(canvas.height))

        //foreground bar
        ctx.fillStyle = '#FF8A80'
        let width = (parseInt(canvas.width)) / maxCount * (parseInt(value))
        ctx.fillRect(0, 0, width, parseInt(canvas.height))
    }

    updateEachMorbidityBar()

    // Event listener for category selection change
    categoryOpt.addEventListener('change', function() {
        updateMorbidityChart(parseInt(categoryOpt.value))
    })
})
