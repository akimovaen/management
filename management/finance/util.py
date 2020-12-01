from datetime import datetime


def view_month(month_delta):
    today = datetime.today()
    year = today.year
    month_to_view = today.month - month_delta or 12
    date_to_view = {'year': year, 'month': month_to_view}

    return date_to_view


def weekdays_in_month(first_weekday, days_in_month):
    weekday_list = []
    weekday_names = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    for day in range(days_in_month):
        weekday = day + first_weekday
        weekday = weekday % 7
        weekday_list.append({"day": day+1, "weekday": weekday_names[weekday]})

    return weekday_list


def month_name(month):
    month_list = ['January', 'February', 'March', 'April',
                  'May', 'June', 'July','August', 'September',
                  'October', 'November', 'December']
    name = month_list[month-1]

    return name


def plus_minus_month(year_month, plus):
    if plus is True:
        if year_month['month'] == 12:
            new_month = 1
            new_year = year_month['year'] + 1
        else:
            new_month = year_month['month'] + 1
            new_year = year_month['year']
    else:
        if year_month['month'] == 1:
            new_month = 12
            new_year = year_month['year'] - 1
        else:
            new_month = year_month['month'] - 1
            new_year = year_month['year']
    
    return {'year': new_year, 'month': new_month}