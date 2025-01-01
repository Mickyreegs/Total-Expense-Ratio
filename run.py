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
    
    print(f"From Date is {from_date_object}")
    print(f"To Date is {to_date_object}")

get_date_range()

nav = SHEET.worksheet("net asset values")

data = nav.get_all_values()

print(data)


    

