document.addEventListener("DOMContentLoaded", () => {
    const back_button = document.getElementById("back");

    back_button.addEventListener("click", () => {

        // mark that we want refresh on next page
        const fallback = document.referrer || "/";
        window.location.href = fallback;
    });
});