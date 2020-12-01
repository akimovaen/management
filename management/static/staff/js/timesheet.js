document.addEventListener('DOMContentLoaded', () => {   
    // Display form to enter data
    document.querySelector('#add-data').onclick = function() {
        document.querySelector('#enter-data').style.display = "block";
        document.querySelector('#add-data').style.display = "none";
    }
});