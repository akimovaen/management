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
    
    // Count number of shops.
    const shops = document.querySelectorAll('.shop').length;

    // Count cost type's total amount for each shop.   
    document.querySelectorAll('.type').forEach(type => {
        const type_id = type.getAttribute('name');
        let is_null = true;
        for (i=0; i<shops; i++) {
            let total = 0;
            document.querySelectorAll(`.type-${type_id}`).forEach(row => {
                const amount = row.querySelector(`.shop-${i+1}`).innerHTML;
                if (row.classList.contains('income')) {
                    total -= parseFloat(amount);
                }
                else {
                    total += parseFloat(amount);
                }
            });
            type.parentElement.querySelector(`.shop-${i+1}`).innerHTML = total.toFixed(2);
            if (total != 0) {is_null = false;}
        }
        if (is_null === true) {
            type.parentElement.style.display = "none";   
        }
    });

    // Count cost's total amount and profit for each shop.   
    for (i=0; i<shops; i++) {
        let total = 0;
        const revenue = parseFloat(document.querySelector('#revenue').querySelector(`.shop-${i+1}`).innerHTML);

        document.querySelectorAll('.type_totals').forEach(type => {
            const amount = type.querySelector(`.shop-${i+1}`).innerHTML;
            total += parseFloat(amount);
        });

        const total_expenses = document.querySelector('#total_expenses');
        total_expenses.querySelector(`.shop-${i+1}`).innerHTML = total.toFixed(2);

        const profit = document.querySelector('#profit');
        profit.querySelector(`.shop-${i+1}`).innerHTML = (revenue - total).toFixed(2);

        if (revenue != 0) {
            document.querySelectorAll('.costs').forEach(cost => {
                const amount = cost.querySelector(`.shop-${i+1}`).innerHTML;
                cost.querySelector(`.shop-${i+1}-percent`).innerHTML = (parseFloat(amount)/revenue*100).toFixed(1).concat('%');
            })
            total_expenses.querySelector(`.shop-${i+1}-percent`).innerHTML = (total/revenue*100).toFixed(1).concat('%');
            profit.querySelector(`.shop-${i+1}-percent`).innerHTML = ((revenue - total)/revenue*100).toFixed(1).concat('%');
        }
    }

    // Define the variable for total revenue.
    var total_revenue = 0;

    // Count monthly results of each cost and type of costs.
    document.querySelector('tbody').querySelectorAll('tr').forEach(row => {
        let result = 0;
        row.querySelectorAll('.amount').forEach(amount => {
            result += parseFloat(amount.innerHTML);
        });
        row.querySelector('.results').innerHTML = result.toFixed(2);
        if (row.getAttribute('id') == 'revenue') {
            total_revenue = result;
        }
        if (total_revenue != 0) {
            row.querySelector('.results-percent').innerHTML = (result/total_revenue*100).toFixed(1).concat('%');
        }
    });
});