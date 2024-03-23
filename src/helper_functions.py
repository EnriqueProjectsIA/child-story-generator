from datetime import datetime as dt
import datetime

def calculate_number_of_years(brith_date:str) -> int:
    """
    Calculate the number of years between birth_date and current_date
    """
    # Convert the string date to a datetime object
    birth_date = dt.strptime(brith_date, "%Y-%m-%d")
    current_date = datetime.date.today()
    number_of_years = current_date.year - birth_date.year
    # Check if the current date has passed the birth date
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        number_of_years -= 1
    return number_of_years
