import getpass
import mysql.connector

password = getpass.getpass("MySQL password: ")
db = mysql.connector.connect(host="localhost", user="root",
                             password=password, database="sfils")
cursor = db.cursor()


def show_age_summary():
    sql = """SELECT AgeRangeLabel, COUNT(*), SUM(TotalCheckouts), SUM(TotalRenewals)
             FROM PATRON_RECORD
             LEFT JOIN AGE_RANGE ON PATRON_RECORD.AgeRangeID = AGE_RANGE.AgeRangeID
             GROUP BY AgeRangeLabel
             ORDER BY AgeRangeLabel"""
    cursor.execute(sql)
    print()
    print("Age range | Patron records | Checkouts | Renewals")
    for label, records, checkouts, renewals in cursor.fetchall():
        if label is None:
            label = "Unknown"
        print(label, "|", records, "|", checkouts, "|", renewals)


def show_library_records():
    name = input("Library name (for example Main or Sunset): ")
    sql = """SELECT PatronRecordID, PatronTypeDefinition, TotalCheckouts, TotalRenewals
             FROM PATRON_RECORD
             JOIN PATRON_TYPE ON PATRON_RECORD.PatronTypeCode = PATRON_TYPE.PatronTypeCode
             JOIN HOME_LIBRARY ON PATRON_RECORD.HomeLibraryCode = HOME_LIBRARY.HomeLibraryCode
             WHERE HomeLibraryDefinition = %s
             ORDER BY TotalCheckouts DESC
             LIMIT 10"""
    cursor.execute(sql, (name,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        print("No records found for that library name.")
        return
    print()
    print("Record ID | Patron type | Checkouts | Renewals")
    for row in rows:
        print(row[0], "|", row[1], "|", row[2], "|", row[3])


def show_one_record():
    record_id = input("Patron record ID: ")
    if not record_id.isdigit():
        print("Please enter a whole number.")
        return
    sql = """SELECT PatronRecordID, PatronTypeDefinition, HomeLibraryDefinition,
                    TotalCheckouts, TotalRenewals
             FROM PATRON_RECORD
             JOIN PATRON_TYPE ON PATRON_RECORD.PatronTypeCode = PATRON_TYPE.PatronTypeCode
             JOIN HOME_LIBRARY ON PATRON_RECORD.HomeLibraryCode = HOME_LIBRARY.HomeLibraryCode
             WHERE PatronRecordID = %s"""
    cursor.execute(sql, (int(record_id),))
    row = cursor.fetchone()
    if row is None:
        print("No record has that ID.")
    else:
        print()
        print("Record ID:", row[0])
        print("Patron type:", row[1])
        print("Home library:", row[2])
        print("Checkouts:", row[3])
        print("Renewals:", row[4])


def update_checkouts():
    record_id = input("Patron record ID to update: ")
    new_total = input("New total checkouts: ")
    if not record_id.isdigit() or not new_total.isdigit():
        print("Please enter whole numbers only.")
        return
    cursor.execute("UPDATE PATRON_RECORD SET TotalCheckouts = %s WHERE PatronRecordID = %s",
                   (int(new_total), int(record_id)))
    db.commit()
    if cursor.rowcount == 0:
        print("No record has that ID (or the value was already the same).")
    else:
        print("Record", record_id, "now has", new_total, "checkouts.")


while True:
    print()
    print("SFILS Menu")
    print("1) Summary by age range")
    print("2) Top records for one library")
    print("3) Update a record's checkouts")
    print("4) Look up one record")
    print("0) Quit")
    choice = input("Choose: ")

    if choice == "1":
        show_age_summary()
    elif choice == "2":
        show_library_records()
    elif choice == "3":
        update_checkouts()
    elif choice == "4":
        show_one_record()
    elif choice == "0":
        break
    else:
        print("Please choose 0, 1, 2, 3 or 4.")

cursor.close()
db.close()
print("Goodbye.")