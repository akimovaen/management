document.addEventListener('DOMContentLoaded', () => {   
    // Display form to enter data
    document.querySelector('#add-data').onclick = function() {
        document.querySelector('#enter-data').style.display = "block";
        document.querySelector('#add-data').style.display = "none";
    }

    // Get the list of costs by type of costs
    document.querySelector('#cost_type').onchange = function() {
        const cost_type = document.querySelector('#cost_type').value;
        const form = document.querySelector('#bank_form');
        var cost_list = document.querySelector('#id_cost');
        let cost_list_len = cost_list.options.length;
        for (i=cost_list_len; i>0; i--) {
            cost_list.options.remove(i);
        }
        var counterparty_list = document.querySelector('#id_counterparty');
        let counterparty_list_len = counterparty_list.options.length;
        for (i=counterparty_list_len; i>0; i--) {
            counterparty_list.options.remove(i);
        }

        fetch(form.getAttribute('filter-cost-type-url'), {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": document.querySelector('#csrf_token').value,
                "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
            },
            body: `type=${cost_type}`})
        .then(response => response.json())
        .then(data => {
            data.costs.forEach(item => {
                let option = document.createElement('option');
                option.value = item['id'];
                option.text = item['name'];
                cost_list.add(option);
                });
            data.counterparty.forEach(item => {
                let option = document.createElement('option');
                option.value = item['id'];
                option.text = item['name'];
                counterparty_list.add(option);
                });
            });
    }
    
    // Count and display Total income, Total expenses and Closing day balance
    document.querySelectorAll('.account').forEach(table => {
            let total_income = 0;
            let total_outcome = 0;
    
            table.querySelectorAll('.income').forEach(amount => {
                total_income += parseFloat(amount.innerHTML);
            });
            table.querySelector('.total_income').innerHTML = total_income.toFixed(2);
    
            table.querySelectorAll('.outcome').forEach(amount => {
                total_outcome += parseFloat(amount.innerHTML);
            });
            table.querySelector('.total_outcome').innerHTML = total_outcome.toFixed(2);
            
            let closing_balance = total_income - total_outcome;
            // table.querySelector('.closing_balance').innerHTML = closing_balance.toFixed(2);
            const form = document.querySelector('#bank_form');
            const account = table.getAttribute('name');
            fetch(form.getAttribute('filter-cost-type-url'), {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": document.querySelector('#csrf_token').value,
                    "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                body: `account=${account}&balance=${closing_balance}`})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    table.querySelector('.closing_balance').innerHTML = closing_balance.toFixed(2);
                    // table.querySelector('.closing_balance').style.color = "blue";
                }
            });
    });
    

   
});