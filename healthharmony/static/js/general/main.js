window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        this.location.reload(true)
        // Re-initialize any JS logic that might not have been executed
    }
});
