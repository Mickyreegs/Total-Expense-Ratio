# TER-ribly Financial TER Program

Welcome,

TER-ribly Financial is a Python terminal prgram, which runs in the Code Institute mock terminal on Heroku.

The live version was deployed to Heroku via GitHub and can be found here:

[TER-ribly Financial](https://ter-ribly-financial-ebc03ebd637e.herokuapp.com/)

![AmIResponsive terminal image of TER-ribly Financial responsiveness](readme/Am%20I%20Responsive.JPG)

## How To Run

Users must select a date range within 2024 and a TER is calculated for that date range based on the following data:
<ul>
    <li>Average NAV
    <li>Fixed Expenses
    <li>Variable Expenses
    <li>Total Expenses
    <li>Day Count
</ul>


![Flow Chart detailing the TER calculation process in the terminal](readme/Lucid%20Chart.png)

## Features

#### Input validation and error checking
<ul>
    <li>Dates must be in dd/mm/yyyy format
    <li>From Date cannot be greater than To Date
    <li>Dates selected must be within the data set provided (2024)
</ul>

![Error 3](readme/Error%203.JPG)

![Error 2](readme/Error%202.JPG)

![Error1](readme/Error%201.JPG)

#### Comprehensive data file with an entire year of NAVs to work from
![Daily NAVs](readme/Daily%20NAVs.JPG)

#### Fixed expenses calculation based on budget data provided
![Fixed Expense Budget](readme/Fixed%20Budget.JPG)

#### Variable expenses calculation based on the prospectus rates provided
![Variable Expense Rates](readme/Variable%20Rates.JPG)

#### Day count based on user date selection
![Day Count](readme/Day%20Count.JPG)

## Data Model
The data model reflects the structure of the Total Expense Ratio (TER) calculations, detailing the basic fund info,
time period, average NAV, expenses and the calculated TER.  The model uses and stores the data within the worksheets.

#### Data calculated in Terminal
![Data returned from Terminal](readme/Returned%20Data%202.JPG)

#### Calculated data pushed to TER worksheet
![TER Worksheet showing the update TER calculation and its inputs](readme/TER.JPG)

#### History of calculated data stored in run history worksheet
![TER history worksheet showing the historic TER calculation runs and their inputs](readme/Run%20History.JPG)

## Testing

### Functional Testing
<table>
    <tr>
        <th>Action</th>
        <th>Expected Behaviour</th>
        <th>Pass/Fail</th>
    </tr>
    <tr>
        <td>Input Validation</td>
        <td>User cannot proceed unless the correct dates and format are used</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>Day Count Calculation</td>
        <td>The correct number of days is calculated based on user inputs</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>Average NAV calculation</td>
        <td>Calculates correct average NAV for date range specified by user</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>Fixed Expense Calculation</td>
        <td>Calculates correct fixed expenses for date range using the budget provided in worksheets</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>Variable Expense Calculation</td>
        <td>Calculates correct variable expenses for date range using the rates provided in worksheets</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>Total Expense Calculation</td>
        <td>Calculates total expenses by adding fixed and variable</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>TER Calculation</td>
        <td>The correct TER is calculated using Total Expenses / Average NAV</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>TER Worksheet Update</td>
        <td>The data is pushed to the TER worksheet and overwrites for every run</td>
        <td>Pass</td>
    </tr>
    <tr>
        <td>TER Run History Worksheet Update</td>
        <td>The data is appended to the run history worksheet and stores all historical TER calculations</td>
        <td>Pass</td>
    </tr>
</table>

### Bugs
Squashed bugs were:
<ul>
    <li>Datetime format - Converting data from string to date, and in dd/mm/yyyy format, proved tough to begin with,
        but this was corrected after reviewing the course materials and the Python.org materials
    <li>Variable Expenses - The calculation was incorrect at the beginning due to the incorrect use of parentheses. 
        The final formula is <strong>total_variable += (average_nav * rate * day_count) / (len(data)-1)</strong>
</ul>

### Remaining Bugs
No bugs remain

### Validator Testing
No errors were returned from the Code Institute's Python Linter [PEP8](https://pep8ci.herokuapp.com/)

![PEP8 Linter results image](readme/PEP8.JPG)

## Deployment
The project was deployed using Code Institute's mock terminal for Heroku.

Steps for deployment were:
<ul>
    <li>Create a new Heroku app
    <li>Set the buildbacks to Python and NodeJS in that order
    <li>Additional step of adding PORT 8000 was implemented as per CI guidelines
    <li>Link the Heroku app to the repository
    <li>Click on Deploy
</ul>

## Credits

Code Institute - Python Essentials

[Code Institute - Love Sandwiches - Essentials Project](https://github.com/Code-Institute-Solutions/love-sandwiches-p5-sourcecode/tree/master/05-deployment/01-deployment-part-1)

[Stack Overflow - General Queries](https://stackoverflow.com/)

[Python.org - Datetime](https://docs.python.org/3/library/datetime.html)

[Python.org - Math](https://docs.python.org/3/library/math.html)
