document.addEventListener('DOMContentLoaded', () => { 
    // Count payment due for each employee.
    document.querySelectorAll('.name').forEach(person => {
        let is_null = true;
        prev_salary = parseFloat(person.querySelector('.prev_salary').innerHTML);
        if (prev_salary != 0) {is_null = false;}
        first_prepayment = parseFloat(person.querySelector('.first_prepayment').innerHTML);
        if (first_prepayment != 0) {is_null = false;}
        first_salary = parseFloat(person.querySelector('.first_salary').innerHTML);
        if (first_salary != 0) {is_null = false;}
        first_payment = person.querySelector('.first_payment_due');
        payment_due = first_salary + prev_salary - first_prepayment;
        first_payment.innerHTML = payment_due.toFixed(2);
        
        paid_salary = parseFloat(person.querySelector('.paid_salary').innerHTML);
        if (paid_salary != 0) {is_null = false;}
        second_prepayment = parseFloat(person.querySelector('.second_prepayment').innerHTML);
        if (second_prepayment != 0) {is_null = false;}
        second_salary = parseFloat(person.querySelector('.second_salary').innerHTML);
        if (second_salary != 0) {is_null = false;}
        second_payment = person.querySelector('.second_payment_due');
        second_payment.innerHTML = (payment_due - paid_salary + second_salary - second_prepayment).toFixed(2);

        if (is_null === true) {
            person.style.display = "none";   
        }
    });
  
});