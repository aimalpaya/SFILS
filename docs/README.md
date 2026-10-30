# Project Documentation

Here, we maintain the documentation of the project.

This includes how to build and run the software, along with any screenshots that can be of help.

This is my version of the San Francisco Integrated Library using Python

Packages used:
pandas
openpyxl
mysql-connector-python

Ensure Mysql is running

How to build and run(Required):
1. Run create_tables.sql using Mysql
2. Set path to excel file in load_data.py and run it "python load_data.py"
3. Should output Inserts and Rows in Excel File:
4. Optional-add index using mysql

How Load Data works:
1. Pandas loads the excel sheet
2. The script fixes the column names and cleans the data
3. Connects to Mysql, password needed
4. The script fills each look up table
5. Mysql assigns age range IDs
6. Then it builds each row by collecting patron values.
7. It inserts 10000 rows at a time until it reaches the number of rows in the xlsx file

How to use app:
1. Ensure that excel data is loaded
2. Type "python app.py" in command line(may need to change file path to app folder)
3. Further instructions in app

Benchmark Details: Type "python benchmark.py" in command line
Benchmark creates normalized and flat table performance values

Analyze Queries: Run in Mysql

benchmark results and queries included in results tab as pngs/text


Problems:
Ran into errors with github commands on personal machine
Errors after using load data when create tables already ran, solution, clear tables before re running

Acknowledgements:
Chatgpt and Gemini was used for assistance in coding and reccommended outputs/helped with errors through and clean up
Was recommended a flat table
 
