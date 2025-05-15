document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("edit-button").addEventListener("click", function() {
        document.getElementById("edit-form-container").style.display = 'block';
        document.querySelector(".form-card").style.display = 'none';
        document.getElementById("edit-button").style.display = 'none';
    });
});
