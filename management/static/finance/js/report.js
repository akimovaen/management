document.addEventListener('DOMContentLoaded', () => {   
    // Get global variables.
    const balance = document.querySelector('#balance').innerHTML;
    const revenue = document.querySelector('#revenue').innerHTML;
    const bank = document.querySelector('#bank').innerHTML;
   
     // Count and display Cash revenue   
    if (document.querySelector(`.item-${revenue}`) && document.querySelector(`.item-${bank}`)) {
        const total_revenue = document.querySelector(`.item-${revenue}`).getElementsByClassName('amount')[0].innerHTML;
        const noncash_revenue = document.querySelector(`.item-${bank}`).getElementsByClassName('amount')[0].innerHTML;
        document.querySelector('#cash-revenue').innerHTML = (total_revenue - noncash_revenue).toFixed(2);    
    }

    // Count and display Total income, Total expenses and Closing day balance
    if (document.querySelector(`.item-${balance}`)) {
        var total_income = 0;
        var total_expense = 0;
    
        document.querySelectorAll('.income').forEach(amount => {
            total_income += parseFloat(amount.innerHTML);
        });
        const openning_balance = document.querySelector(`.item-${balance}`).getElementsByClassName('amount')[0].innerHTML;
        total_income += parseFloat(openning_balance);

        document.querySelector('#total-income').innerHTML = total_income.toFixed(2);
    
        document.querySelectorAll('.expense').forEach(amount => {
            total_expense += parseFloat(amount.innerHTML);
        });
        document.querySelector('#total-expense').innerHTML = total_expense.toFixed(2);
        document.querySelector('#closing-balance').innerHTML = (total_income - total_expense).toFixed(2);
        document.querySelector('#send-closing-balance').value = (total_income - total_expense).toFixed(2);
    
    }
    
    // Display form to enter data
    document.querySelector('#add-data').onclick = function() {
        document.querySelector('#enter-data').style.display = "block";
        document.querySelector('#add-data').style.display = "none";
    }
    
    // Get the list of costs by type of costs
    document.querySelector('#cost_type').onchange = function() {
        const cost_type = document.querySelector('#cost_type').value;
        const form = document.querySelector('#report_form');
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
});