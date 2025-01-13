import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('ter_data')

nav = SHEET.worksheet("net asset values")  # pull NAV data from Google Sheets
data = nav.get_all_values()


fixed = SHEET.worksheet("budget")  # Pull fixed expense values
f_data = fixed.get_all_values()


variable = SHEET.worksheet("prospectus rates")  # Pull variable rate data
v_data = variable.get_all_values()


def get_fund_info(data):
    """
    Pulls fund name and fund number from the list of data
    """
    fund_number = None
    fund_name = None

    for row in data[1:]:  # skips top row of data list in for loop
        fund_number = row[1]  # takes the values in the second column
        fund_name = row[2]  # takes the values in the 3rd column

    return fund_number, fund_name


def get_date_range():
    """
    Asks user to select a date range to run the TER calculation.
    The user submits dd/mm/yyyy and this is converted using datetime.
    Try/Except used to ensure the user inputs a correct date format
    """

    # Check user dates against available dates in the nav worksheet
    date_column = [row[0] for row in data]
    available_dates = {
        datetime.strptime(date, '%d/%m/%Y').date() for date in date_column[1:]
    }

    while True:
        try:
            from_date_str = input("From Date (dd/mm/yyyy): \n")

            # Change string to date format
            from_date_object = datetime.strptime(
                from_date_str,
                '%d/%m/%Y'
            ).date()

            to_date_str = input("To Date (dd/mm/yyyy): \n")

            # Change string to date format
            to_date_object = datetime.strptime(
                to_date_str,
                '%d/%m/%Y'
            ).date()

            # From date must be less than to date
            if from_date_object >= to_date_object:
                print("From Date must be less than To Date...")
                continue

            # Verifies user entry against available data
            if (
                from_date_object not in available_dates
                or to_date_object not in available_dates
            ):
                print("One or both dates not found.  Select 2024 dates")
                continue

            return from_date_object, to_date_object, from_date_str, to_date_str

        except ValueError as e:
            print(f"Invalid date format: {e}.  Format should be dd/mm/yyyy.")


def filter_nav_by_date_range(
    data,
    from_date,
    to_date
):
    """
    Filters the NAVs for the date range specified by the user.
    The filtered NAVs can then be used to get the average NAV for that period
    """
    header = data[0]
    date_index = header.index("Date")
    nav_index = header.index("Net Asset Value")

    filtered_navs = []
    for row in data[1:]:
        row_date = datetime.strptime(row[date_index], "%d/%m/%Y").date()
        if from_date <= row_date <= to_date:
            filtered_navs.append(float(row[nav_index].replace(',', '')))
    return filtered_navs


def calculate_fixed_expenses_for_period(
    f_data,
    data,
    day_count
):
    """
    Sums the fixed expenses on the worksheet, divides that amount by the total
    rows in the net asset values worksheet (minus 1 for the header),
    and finally multiplies the result by the day count
    """
    total_fixed = 0
    for fees in f_data[1:]:
        budget = int(fees[1])
        total_fixed += budget
    total_fixed = (total_fixed / (len(data)-1)) * day_count
    return total_fixed


def calculate_total_variable_fees(
    v_data,
    data,
    day_count,
    average_nav
):
    """
    With the date range selected by the user,
    the variable expenses (rate*average NAV*day count)/366
    will be calculated for the period and used as part of the TER calculation
    """
    header = v_data[0]
    expense_index = header.index("Expense Type")
    rate_index = header.index("Rate")

    variable_rates = []
    for row in v_data[1:]:
        expense = row[expense_index]
        rate = row[rate_index]
        if isinstance(rate, str) and '%' in rate:  # check rate is string & '%'
            rate = float(rate.strip('%')) / 100  # strips %, converts to float
        else:
            rate = float(rate)
        variable_rates.append(round(rate, 4))  # append to 4 decimal places

    # Multiplies sum of var rates (average NAV * rate * day count / 366)
    total_variable = 0
    for rate in variable_rates:
        total_variable += (average_nav * rate * day_count) / (len(data)-1)

    return variable_rates, total_variable


def format_number(number):
    """
    Amend number format for use in TER worksheet
    """
    return "{:,.2f}".format(number)  # returns number to 2 decimals


def format_percent(number):
    return "{:.4f}%".format(number)  # returns number to 4 decimals with '%'


def insert_results(
    ter_sheet,
    ter_history,
    fund_number,
    fund_name,
    from_date_str,
    to_date_str,
    day_count,
    average_nav,
    total_fixed_expenses,
    total_variable_expenses,
    ter
):
    """
    Inserts all function results to the TER worksheet in the expected formats
    """
    average_nav_format = format_number(average_nav)
    total_fixed_expenses_format = format_number(total_fixed_expenses)
    total_variable_expenses_format = format_number(total_variable_expenses)
    ter_format = format_percent(ter)

    ter_row = [
        fund_number,
        fund_name,
        from_date_str,
        to_date_str,
        day_count,
        average_nav_format,
        total_fixed_expenses_format,
        total_variable_expenses_format,
        ter_format
    ]

    # Overwrites row 2 on the TER worksheet
    ter_sheet.update(range_name='A2:I2', values=[ter_row])
    # Append latest result to create history of runs in run history worksheet
    ter_history.append_row(ter_row)


def main():
    """
    Calls all of the functions and returns the results.
    """
    from_date, to_date, from_date_str, to_date_str = get_date_range()
    day_count = (to_date - from_date).days+1
    print(f"\nDay count for the period is {day_count}\n")

    fund_number, fund_name = get_fund_info(data)
    print(f"Fund number: {fund_number}\n")
    print(f"Fund name: {fund_name}\n")

    # Gets the NAVs available for that date range
    filtered_navs = filter_nav_by_date_range(data, from_date, to_date)

    # If filtered NAVs available, calculate average NAV (ANA) for that period
    if filtered_navs:
        average_nav = sum(filtered_navs) / len(filtered_navs)
        print(
            f"ANA from {from_date} to {to_date} is €{average_nav:,.2f}\n"
        )
    else:
        print("No data available for that date range....\n")

    # Calculates fixed expenses for the period defined by user
    total_fixed_expenses = calculate_fixed_expenses_for_period(
        f_data,
        data,
        day_count
    )

    print(
        f"Fixed fees for the period were €{total_fixed_expenses: ,.2f}\n"
    )

    # Calculates variable expenses for the period defined by user
    variable_rates, total_variable_expenses = calculate_total_variable_fees(
        v_data,
        data,
        day_count,
        average_nav
    )

    print(
        f"Variable fees for the period were €{total_variable_expenses: ,.2f}\n"
    )

    # Calculates total expenses for the period defined by user
    total_expenses = total_fixed_expenses + total_variable_expenses
    print(f"Total fees for the period were €{total_expenses: ,.2f}\n")

    # Calculates total expense ratio (TER)
    ter = (total_expenses / average_nav) * 100
    print(f"Total Expense Ratio for the period is{ter: .4f}%\n")

    # Pushes results to the TER worksheet
    ter_sheet = SHEET.worksheet("TER")  # TER worksheet
    ter_history = SHEET.worksheet("run history")  # TER History worksheet
    insert_results(
        ter_sheet,
        ter_history,
        fund_number,
        fund_name,
        from_date_str,
        to_date_str,
        day_count,
        average_nav,
        total_fixed_expenses,
        total_variable_expenses,
        ter
    )


print("Launching TER program....\n")
print("Select date range within 2024 for your TER:\n")
main()
