document.addEventListener('DOMContentLoaded', () => {   
    // Count cost type's total amount per day.   
    document.querySelectorAll('.name').forEach(name => {
        let is_null = true;
        let total = 0;
        name.querySelectorAll('.amount').forEach(day => {
            const amount = day.innerHTML;
            total += parseFloat(amount);
        });
        name.querySelector('.results').innerHTML = total.toFixed(1);
        if (total != 0) {is_null = false;}
        if (is_null === true) {
            name.style.display = "none";   
        }
    });
});