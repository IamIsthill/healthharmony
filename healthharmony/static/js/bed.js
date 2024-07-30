fetch('/api/data/')
    .then((response) => {
    if (!response.ok) {
        throw new Error('Network response was not ok')
    }
    return response.json()
    })
    .then((data) => {
    console.log('Data received:', data)
    })
    .catch((error) => {
    console.error('There was a problem with the fetch operation:', error)
    })
    let scanner = new Scanner({
        // Provide options as needed
        video: document.querySelector('#videoElement'), // Assuming you have a video element with id 'videoElement'
        captureImage: true,
        scanPeriod: 1,
        refractoryPeriod: 5000, // 5 seconds
        continuous: true,
        mirror: true,
        backgroundScan: false
    });

    // Start scanning
    scanner.start();
