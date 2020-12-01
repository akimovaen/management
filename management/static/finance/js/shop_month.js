document.addEventListener('DOMContentLoaded', () => {   
    // Display rows with data by costs.
    document.querySelectorAll('.display_list').forEach(plus => {
        plus.onclick = function() {
            const type = plus.nextElementSibling.getAttribute('name');
            document.querySelectorAll(`.type-${type}`).forEach(row => {
                if (row.style.display == "table-row"){
                    row.style.display = "none";
                }
                else {
                    row.style.display = "table-row";
                }
            });
        }
    });

    // Count number of days this month.
    const days = (document.querySelector('#weekdays').innerHTML.split(',')).length/2;
    
    // Count cost type's total amount per day.   
    document.querySelectorAll('.type').forEach(type => {
        const type_id = type.getAttribute('name');
        let is_null = true;
        for (i=0; i<days; i++) {
            let total = 0;
            document.querySelectorAll(`.type-${type_id}`).forEach(row => {
                const amount = row.querySelector(`.day-${i+1}`).innerHTML;
                if (row.querySelector('.cost_name').innerHTML == "Opening day balance" ||
                    row.querySelector('.cost_name').innerHTML == "Cash revenue") {
                        total += parseFloat(amount);
                    }
                else {
                    if (row.classList.contains('income')) {
                        total -= parseFloat(amount);
                    }
                    else {
                        total += parseFloat(amount);
                    }
                }
            });
            type.parentElement.querySelector(`.day-${i+1}`).innerHTML = total.toFixed(2);
            if (total != 0) {is_null = false;}
        }
        if (is_null === true) {
            type.parentElement.style.display = "none";   
        }
    });
    
    // Define the rows of closing day balance and opening day balance.
    const close_balance = document.querySelector('.closing_balance');
    const open_balance_id = document.querySelector('#balance').innerHTML;
    const open_balance = document.querySelector(`.type-${open_balance_id}`).previousElementSibling;

    // Count closing day balance per day and check that it's equal to the opening balance of the next day.
    for (i=0; i<days; i++) {
        let total = 0;
        document.querySelectorAll('.income').forEach(income => {
            const amount = income.querySelector(`.day-${i+1}`).innerHTML;
            total += parseFloat(amount);
        });
        document.querySelectorAll('.expense').forEach(expense => {
            const amount = expense.querySelector(`.day-${i+1}`).innerHTML;
            total -= parseFloat(amount);
        });
        close_balance.querySelector(`.day-${i+1}`).innerHTML = total.toFixed(2);
        
        if (i > 0) {
            if (open_balance.querySelector(`.day-${i+1}`).innerHTML != close_balance.querySelector(`.day-${i}`).innerHTML) {
                open_balance.querySelector(`.day-${i+1}`).style.color = "crimson";
            }
        }
    }

    // Count monthly results of each cost and type of costs except for opening and closing day balances.
    document.querySelector('tbody').querySelectorAll('tr').forEach(row => {
        if (row.querySelector('.type')) {
            const type_cost = row.querySelector('.type').getAttribute('name');
            if (type_cost != open_balance_id) {
                result = 0
                row.querySelectorAll('.amount').forEach(amount => {
                    result += parseFloat(amount.innerHTML);
                });
                row.querySelector('.results').innerHTML = result.toFixed(2);
            }
        }
        else {
            if (!row.classList.contains(`.type-${open_balance_id}`)) {
            result = 0
            row.querySelectorAll('.amount').forEach(amount => {
                result += parseFloat(amount.innerHTML);
            });
            row.querySelector('.results').innerHTML = result.toFixed(2);
            }
        }
    });
});