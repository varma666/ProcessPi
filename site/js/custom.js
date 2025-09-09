document.addEventListener("DOMContentLoaded", function() {
    const header = document.querySelector(".md-header__inner");
    if (header) {
        header.setAttribute("data-tagline", "{{ config.extra.tagline }}");
    }
});
