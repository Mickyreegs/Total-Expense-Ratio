import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('ter_data')

def get_average_nav():
    """
    Get the average net asset value within the date range specified by the user
    """
    print("Select date range for your TER:")

    from_date_str = input("From Date:")
    to_date_str = input("To Date:")
    print(f"From Date is {from_date_str}")
    print(f"To Date is {to_date_str}")

    

get_average_nav()