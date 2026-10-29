import getpass
import time
import mysql.connector
 
password = getpass.getpass("MySQL password: ")
db = mysql.connector.connect(host="localhost", user="root",
                             password=password, database="sfils")
cursor = db.cursor()
 
 
def time_query(sql):
    total = 0
    for i in range(5):
        start = time.time()
        cursor.execute(sql)
        cursor.fetchall()
        total = total + (time.time() - start)
    return total / 5 * 1000
 
 
print("Building the flat table...")
cursor.execute("DROP TABLE IF EXISTS PATRON_FLAT")
cursor.execute("""CREATE TABLE PATRON_FLAT AS
    SELECT PatronRecordID, PatronTypeDefinition, AgeRangeLabel,
           HomeLibraryDefinition, NotificationDefinition,
           TotalCheckouts, TotalRenewals, YearRegistered
    FROM PATRON_RECORD
         JOIN PATRON_TYPE ON PATRON_RECORD.PatronTypeCode = PATRON_TYPE.PatronTypeCode
         LEFT JOIN AGE_RANGE ON PATRON_RECORD.AgeRangeID = AGE_RANGE.AgeRangeID
         JOIN HOME_LIBRARY ON PATRON_RECORD.HomeLibraryCode = HOME_LIBRARY.HomeLibraryCode
         JOIN NOTIFICATION_PREFERENCE
              ON PATRON_RECORD.NotificationCode = NOTIFICATION_PREFERENCE.NotificationCode""")
 
normalized_library = """SELECT HomeLibraryDefinition, SUM(TotalCheckouts)
    FROM PATRON_RECORD JOIN HOME_LIBRARY
         ON PATRON_RECORD.HomeLibraryCode = HOME_LIBRARY.HomeLibraryCode
    GROUP BY HomeLibraryDefinition"""
flat_library = """SELECT HomeLibraryDefinition, SUM(TotalCheckouts)
    FROM PATRON_FLAT GROUP BY HomeLibraryDefinition"""
 
normalized_age = """SELECT AgeRangeLabel, SUM(TotalCheckouts)
    FROM PATRON_RECORD LEFT JOIN AGE_RANGE
         ON PATRON_RECORD.AgeRangeID = AGE_RANGE.AgeRangeID
    GROUP BY AgeRangeLabel"""
flat_age = """SELECT AgeRangeLabel, SUM(TotalCheckouts)
    FROM PATRON_FLAT GROUP BY AgeRangeLabel"""
 
print()
print("Simulating 5 runs")
print("Question                 | Normalized | Flat table")
print("Checkouts per library    |", round(time_query(normalized_library), 1),"ms", "|", round(time_query(flat_library), 1),"ms")
print("Checkouts per age range  |", round(time_query(normalized_age), 1), "ms", "|", round(time_query(flat_age), 1),"ms")
 
# ---------- Clean up ----------
cursor.execute("DROP TABLE PATRON_FLAT")
db.commit()
cursor.close()
db.close()
print()
print("Done.")
 