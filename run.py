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

#pull NAV data from Google Sheets
nav = SHEET.worksheet("net asset values")
data = nav.get_all_values()

#Pull fixed expense values from Google Sheets
fixed = SHEET.worksheet("budget")
f_data = fixed.get_all_values()

#Pull variable expense rate data from Google Sheets
variable = SHEET.worksheet("prospectus rates")
v_data = variable.get_all_values()

def get_fund_info(data):
    """
    Pulls fund name and fund number from the list of data
    """
    fund_number = None
    fund_name = None

    for row in data[1:]: #skips top row of data list in for loop
        fund_number = row[1] #takes the values in the second column
        fund_name = row[2] #takes the values in the 3rd column
    
    return fund_number, fund_name

def get_date_range():
    """
    Asks user to select a date range to run the Total Expense Ratio calculation.
    The user submits dd/mm/yyyy and this is converted using datetime.
    Try/Except is used to ensure the user inputs a correct date in the expected format
    """


    #Check user selected dates against available dates in the nav worksheet
    date_column = [row[0] for row in data]
    available_dates = {datetime.strptime(date, '%d/%m/%Y').date() for date in date_column[1:]}
    
    while True:
        try:
            from_date_str = input("From Date (dd/mm/yyyy): \n")
            from_date_object = datetime.strptime(from_date_str, '%d/%m/%Y').date() #change string to date format

            to_date_str = input("To Date (dd/mm/yyyy): \n")
            to_date_object = datetime.strptime(to_date_str, '%d/%m/%Y').date() #change string to date format

            if from_date_object >= to_date_object: #from date must be less than to date
                print("From Date must be less than To Date.  Please select valid dates")
                continue

            if from_date_object not in available_dates or to_date_object not in available_dates: #verifies user entry against available data
                print("One or both dates not found in data.  Please select dates within 2024")
                continue

            return from_date_object, to_date_object, from_date_str, to_date_str

        except ValueError as e:
            print(f"Invalid date format: {e}.  Please enter the date as dd/mm/yyyy.")


def filter_nav_by_date_range(data, from_date, to_date):
    """
    Filters the NAVs for the date range specified by the user.
    The filtered NAVs can then be used to get the average NAV for that period
    """
    header = data[0]
    date_index = header.index("Date")
    nav_index = header.index("Net Asset Value")

    filtered_navs = []
    for row in data[1:]: #skips top row of data list in for loop
        row_date = datetime.strptime(row[date_index], "%d/%m/%Y").date() #converts data to date format
        if from_date <= row_date <= to_date: #filters for specified dates
            filtered_navs.append(float(row[nav_index].replace(',', ''))) #appends NAV in float format
    return filtered_navs


def calculate_fixed_expenses_for_period(f_data, data, day_count):
    """
    Sums all the fixed expenses on the worksheet, then divides that amount by the total
    rows in the net asset values worksheet (minus 1 for the header)
    and finally multiplies the result by the day count
    """
    total_fixed = 0
    for fees in f_data[1:]: #skips top row of data list in for loop
        budget = int(fees[1]) #takes the values at index 1 on the 'budget' worksheet and converts to integers
        total_fixed += budget #sums the budget amounts
    total_fixed = (total_fixed / (len(data)-1)) * day_count #Takes the total_fixed, divides by length of 'data' (366days), and multiplies by user range (day count)
    return total_fixed


def calculate_total_variable_fees(v_data, data, day_count, average_nav):
    """
    With the date range selected by the user, 
    the variable expenses (rate*average NAV*day count)/366
    will be calculated for the period and used as part of the TER calculation 
    """
    header = v_data[0]
    expense_index = header.index("Expense Type")
    rate_index = header.index("Rate")

    variable_rates = []
    for row in v_data[1:]:#skips top row of data list in for loop
        expense = row[expense_index]
        rate = row[rate_index]
        if isinstance(rate, str) and '%' in rate: #checks if rate is both a string and contains '%'
            rate = float(rate.strip('%')) / 100  #strips the % sign and converts to float
        else:
            rate = float(rate)
        variable_rates.append(round(rate,4)) #append to 4 decimal places

    total_variable = 0
    for rate in variable_rates:
        total_variable += (average_nav * rate * day_count) / (len(data)-1) #Gets the sum of the variable rates by multiplying average NAV by rate by day count and dividing by 366

    return variable_rates, total_variable


def format_number(number):
    """
    Amend number format for use in TER worksheet
    """
    return "{:,.2f}".format(number)

def format_percent(number):
    return "{:.4f}%".format(number)


def insert_results(ter_sheet, fund_number, fund_name, from_date_str, to_date_str, day_count, average_nav, total_fixed_expenses, total_variable_expenses, ter):
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

    ter_sheet.insert_row(ter_row, 2)

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

    #Gets the NAVs available for that date range
    filtered_navs = filter_nav_by_date_range(data, from_date, to_date)
    #If filtered NAVs available, calculate the average NAV for that period
    if filtered_navs:
        average_nav = sum(filtered_navs) / len(filtered_navs)
        print(f"Average Net Assets for the period {from_date} to {to_date} is €{average_nav:,.2f}\n")
    else:
        print("No data available for that date range....\n")

    #calculates fixed expenses for the period defined by user
    total_fixed_expenses = calculate_fixed_expenses_for_period(f_data, data, day_count)
    print(f"Fixed expenses for the period were €{total_fixed_expenses: ,.2f}\n")

    #calculates variable expenses for the period defined by user
    variable_rates, total_variable_expenses = calculate_total_variable_fees(v_data, data, day_count, average_nav)
    print(f"Variable expenses for the period were €{total_variable_expenses: ,.2f}\n")

    #calculates total expenses for the period defined by user
    total_expenses = total_fixed_expenses + total_variable_expenses
    print(f"Total expenses for the period were €{total_expenses: ,.2f}\n")

    #calculates total expense ratio (TER)
    ter = (total_expenses / average_nav) * 100
    print(f"Total Expense Ratio for the period was {ter: .4f}%\n")

    #pushes results to the TER worksheet
    ter_sheet = SHEET.worksheet("TER") #TER worksheet
    insert_results(ter_sheet, fund_number, fund_name, from_date_str, to_date_str, day_count, average_nav, total_fixed_expenses, total_variable_expenses, ter)
    
    

print("Launching TER program....\n")
print("Select date range within 2024 for your TER:\n")
main()

    


    
