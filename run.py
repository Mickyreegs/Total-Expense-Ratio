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

def get_date_range():
    """
    Get the date range specified by the user to build the report
    """
    print("Select date range for your TER:")

    from_date_str = input("From Date (dd/mm/yyyy): ")
    from_date_object = datetime.strptime(from_date_str, '%d/%m/%Y').date()

    to_date_str = input("To Date (dd/mm/yyyy): ")
    to_date_object = datetime.strptime(to_date_str, '%d/%m/%Y').date()

    return from_date_object, to_date_object


from_date, to_date = get_date_range()
print(f"From Date: {from_date}")
print(f"To Date: {to_date}")

nav = SHEET.worksheet("net asset values")

def get_average_nav(nav):
    """
    Using the Net Asset Value column in the net asset values tab,
    we iterate through the lists to extract all NAVs and get a single average figure
    """
    data = nav.get_all_values()
    header = data[0]
    nav_index = header.index("Net Asset Value")
    nav_values = [float(row[nav_index].replace(',', '')) for row in data[1:]]
    average_nav = sum(nav_values) / len(nav_values)
    return average_nav

average_nav = get_average_nav(nav)
print(f"The average NAV is: €{average_nav}")



    

