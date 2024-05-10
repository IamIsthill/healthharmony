document.addEventListener("DOMContentLoaded", function() {
    fetchSectionContent("herosection.html", "section1Content");
    fetchSectionContent("bedspace.html", "section2Content");
});

function fetchSectionContent(url, targetId) {
    fetch(url)
    .then(response => response.text())
    .then(data => {
        document.getElementById(targetId).innerHTML = data;
    })
    .catch(error => console.error("Error fetching section content:", error));
}