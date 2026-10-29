import getpass
import pandas as pd
import mysql.connector
 
FILE_NAME = r"C:\path\to\SFPL_DataSF_library-usage_Jan_2023.xlsx"   # change to path of excel file
 
print("Reading xlsx file...")
df = pd.read_excel(FILE_NAME)
 

df.columns = [name.split("\n")[0].strip() for name in df.columns]
 

text_columns = ["Patron Type Definition", "Age Range", "Home Library Code",
                "Home Library Definition", "Circulation Active Month",
                "Notification Preference Code", "Notification Code Definition"]
for column in text_columns:
    df[column] = df[column].str.strip()
 

df["Home Library Code"] = df["Home Library Code"].fillna("none")
df["Home Library Definition"] = df["Home Library Definition"].fillna("Unknown")
# The notification code '-' has no definition in the data.
df["Notification Code Definition"] = df["Notification Code Definition"].fillna("Not specified")
 

password = getpass.getpass("MySQL password: ")
db = mysql.connector.connect(host="localhost", user="root",
                             password=password, database="sfils")
cursor = db.cursor()

#Suggested for preventing duplicates: Chatgpt 
print("Cleaning existing database tables...")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE PATRON_RECORD;")
cursor.execute("TRUNCATE TABLE PATRON_TYPE;")
cursor.execute("TRUNCATE TABLE HOME_LIBRARY;")
cursor.execute("TRUNCATE TABLE NOTIFICATION_PREFERENCE;")
cursor.execute("TRUNCATE TABLE AGE_RANGE;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
db.commit()
 
patron_types = df.drop_duplicates(subset="Patron Type Code")
for index, row in patron_types.iterrows():
    cursor.execute(
        "INSERT INTO PATRON_TYPE (PatronTypeCode, PatronTypeDefinition) VALUES (%s, %s)",
        (int(row["Patron Type Code"]), row["Patron Type Definition"]))
 
libraries = df.drop_duplicates(subset="Home Library Code")
for index, row in libraries.iterrows():
    cursor.execute(
        "INSERT INTO HOME_LIBRARY (HomeLibraryCode, HomeLibraryDefinition) VALUES (%s, %s)",
        (row["Home Library Code"], row["Home Library Definition"]))
 
notices = df.drop_duplicates(subset="Notification Preference Code")
for index, row in notices.iterrows():
    cursor.execute(
        "INSERT INTO NOTIFICATION_PREFERENCE (NotificationCode, NotificationDefinition) VALUES (%s, %s)",
        (row["Notification Preference Code"], row["Notification Code Definition"]))
 

for label in sorted(df["Age Range"].dropna().unique()):
    cursor.execute("INSERT INTO AGE_RANGE (AgeRangeLabel) VALUES (%s)", (label,))
db.commit()
 

cursor.execute("SELECT AgeRangeLabel, AgeRangeID FROM AGE_RANGE")
age_ids = {}
for label, age_id in cursor.fetchall():
    age_ids[label] = age_id
 
print("Lookup tables filled.")
 

records = []
for index, row in df.iterrows():
    age_id = age_ids.get(row["Age Range"])         
 
    month = row["Circulation Active Month"]
    if pd.isna(month) or month == "":
        month = None                               
 
    year = row["Circulation Active Year"]
    if pd.isna(year):
        year = None                                  
    else:
        year = int(year)
 
    provided_email = str(row["Provided Email Address"]).lower() == "true"
    in_sf = str(row["Within San Francisco County"]).lower() == "true"
 
    records.append((int(row["Patron Type Code"]), age_id,
                    row["Home Library Code"], row["Notification Preference Code"],
                    int(row["Total Checkouts"]), int(row["Total Renewals"]),
                    month, year, provided_email, in_sf,
                    int(row["Year Patron Registered"])))
 
sql = """INSERT INTO PATRON_RECORD
         (PatronTypeCode, AgeRangeID, HomeLibraryCode, NotificationCode,
          TotalCheckouts, TotalRenewals, CirculationActiveMonth,
          CirculationActiveYear, ProvidedEmail, WithinSFCounty, YearRegistered)
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
 

chunk_size = 10000
for start in range(0, len(records), chunk_size):
    cursor.executemany(sql, records[start:start + chunk_size])
    db.commit()
    print("Inserted", min(start + chunk_size, len(records)), "of", len(records))
 

cursor.execute("SELECT COUNT(*) FROM PATRON_RECORD")
print("Rows in the Excel file:", len(df))
print("Rows in PATRON_RECORD: ", cursor.fetchone()[0])
 
cursor.close()
db.close()
