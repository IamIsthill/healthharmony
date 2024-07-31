document.querySelectorAll('header a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        const sectionId = this.getAttribute('href').substring(1);
        const section = document.getElementById(sectionId);

        if (section) {
            const scrollTop = window.scrollY || window.pageYOffset;
            const sectionTop = section.getBoundingClientRect().top + scrollTop;
            const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

            window.scrollTo({
                top: sectionTop - (viewportHeight / 6.4),
                behavior: 'smooth'
            });
        }
    });
});
