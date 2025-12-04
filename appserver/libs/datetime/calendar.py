from datetime import date, timedelta

def get_start_weekday_of_month(year, month):
    result = date(year, month, 1)
    return result.weekday()

def get_last_day_of_month(year, month):
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    result = next_month - timedelta(days=1)
    return result.day

def get_range_days_of_month(year, month):
    # Get the starting weekday of the month
    start_weekday = get_start_weekday_of_month(year, month)

    # Get the last day of the month
    last_day = get_last_day_of_month(year, month)

    # Convert Monday = 0 to Monday = 1 (to makr Sunday = 0)
    start_weekday = (start_weekday + 1) % 7

    # Create a result list
    result = [0] * start_weekday

    # Add days from the 1st to the last day of the month
    # for day in range(1, last_day + 1):
        # result.append(day)

    return result + list(range(1, last_day + 1))