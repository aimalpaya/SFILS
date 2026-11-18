import pandas as pd
import pymongo

FILE_NAME = r"C:\path\to\your\SFPL_DataSF_library-usage_Jan_2023.xlsx"   # change to path of excel file

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


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["sfils"]
mycol = db["PATRON_RECORDS"]


mycol.drop()


records = []
for index, row in df.iterrows():
    month = row["Circulation Active Month"]
    if pd.isna(month) or month == "":
        month = None

    year = row["Circulation Active Year"]
    if pd.isna(year):
        year = None
    else:
        year = int(year)

    age_range = row["Age Range"]
    if pd.isna(age_range):
        age_range = None

    records = {
        "_id": int(index) + 1,
        "patronTypeCode": int(row["Patron Type Code"]),
        "patronType": row["Patron Type Definition"],
        "ageRange": age_range,
        "homeLibraryCode": row["Home Library Code"],
        "homeLibrary": row["Home Library Definition"],
        "notificationCode": row["Notification Preference Code"],
        "notificationPreference": row["Notification Code Definition"],
        "totalCheckouts": int(row["Total Checkouts"]),
        "totalRenewals": int(row["Total Renewals"]),
        "circulationActiveMonth": month,
        "circulationActiveYear": year,
        "providedEmail": str(row["Provided Email Address"]).lower() == "true",
        "withinSFCounty": str(row["Within San Francisco County"]).lower() == "true",
        "yearRegistered": int(row["Year Patron Registered"]),
    }

    
    records = {key: value for key, value in records.items() if value is not None}
    records.append(records)


chunk_size = 10000
for start in range(0, len(records), chunk_size):
    mycol.insert_many(records[start:start + chunk_size])
    print("Inserted", min(start + chunk_size, len(records)), "of", len(records))

print("Rows in the Excel file:      ", len(df))
print("Records in PATRON_RECORDS:     ", mycol.count_records({}))

myclient.close()