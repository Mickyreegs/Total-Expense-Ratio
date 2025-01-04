import gspread
from google.oauth2.service_account import Credentials
import statistics
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

#Pull fixed expense values from column in Google Sheets
fixed = SHEET.worksheet("budget")
f_data = fixed.get_all_values()

#Pull variable expense rate data from Google Sheets
variable = SHEET.worksheet("prospectus rates")
v_data = variable.col_values(2)

#TER worksheet
ter = SHEET.worksheet("TER")

def get_date_range():
    """
    Asks user to select a date range to run the Total Expense Ratio calculation.
    The user submits dd/mm/yyyy and this is converted using datetime.
    Try/Except is used to ensure the user inputs a correct date in the expected format
    """
    print("Select date range for your TER:")

    while True:
        try:
            from_date_str = input("From Date (dd/mm/yyyy): ")
            from_date_object = datetime.strptime(from_date_str, '%d/%m/%Y').date()

            to_date_str = input("To Date (dd/mm/yyyy): ")
            to_date_object = datetime.strptime(to_date_str, '%d/%m/%Y').date()

            if from_date_object >= to_date_object:
                print("From Date must be less than To Date.  Please select valid dates")
                continue

            return from_date_object, to_date_object

        except ValueError as e:
            print(f"Invalid date format: {e}.  Please enter the date as dd/mm/yyyy.")


from_date, to_date = get_date_range()
day_count = (to_date - from_date).days+1

print(f"Day count for the period is {day_count}\n")



def filter_nav_by_date_range(data, from_date, to_date):
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

#Gets the NAVs available for that date range
filtered_navs = filter_nav_by_date_range(data, from_date, to_date)

#If filtered NAVs available, calculate the average NAV for that period
if filtered_navs:
    average_nav = sum(filtered_navs) / len(filtered_navs)
    print(f"Average Net Assets for the period {from_date} to {to_date} is €{average_nav:,.2f}\n")
else:
    print("No data available for that date range...")


def calculate_fixed_expenses_for_period(f_data, data, day_count):
    total_fixed = 0
    for fees in f_data[1:]:
        budget = int(fees[1])
        total_fixed += budget
    total_fixed = (total_fixed / (len(data)-1)) * day_count
    return total_fixed

total_fixed_expenses = calculate_fixed_expenses_for_period(f_data, data, day_count)
print(f"Total fixed expenses for the period were €{total_fixed_expenses: ,.2f}")


#def calculate_variable_expenses_for_period():
    #"""
    #With the date range selected by the user, the variable expenses will be calculated
    #for the period and used as part of the TER calculation
    #"""



#def calculate_total_expense_ratio():
    #"""
    #This is the final calculation.  TER ratio is (total expenses / average NAV)
    #"""


