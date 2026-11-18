import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["sfils"]
mycol = mydb["patron_records"]


def show_age_summary():
    pipeline = [
        {"$group": {"_id": "$ageRange",
                    "records": {"$sum": 1},
                    "checkouts": {"$sum": "$totalCheckouts"},
                    "renewals": {"$sum": "$totalRenewals"}}},
        {"$sort": {"_id": 1}}
    ]
    print()
    print("Age range | Patron records | Checkouts | Renewals")
    for row in mycol.aggregate(pipeline):
        label = row["_id"]
        if label is None:
            label = "Unknown"      # these documents have no ageRange field
        print(label, "|", row["records"], "|", row["checkouts"], "|", row["renewals"])


def show_library_records():
    name = input("Library name (for example Main or Sunset): ")
    results = mycol.find({"homeLibrary": name}).sort("totalCheckouts", -1).limit(10)
    rows = list(results)
    if len(rows) == 0:
        print("No records found for that library name.")
        return
    print()
    print("Record ID | Patron type | Checkouts | Renewals")
    for doc in rows:
        print(doc["_id"], "|", doc["patronType"], "|", doc["totalCheckouts"], "|", doc["totalRenewals"])


def show_one_record():
    record_id = input("Patron record ID: ")
    if not record_id.isdigit():
        print("Please enter a whole number.")
        return
    doc = mycol.find_one({"_id": int(record_id)})
    if doc is None:
        print("No record has that ID.")
        return
    print()
    print("Record ID:", doc["_id"])
    print("Patron type:", doc["patronType"])
    print("Age range:", doc.get("ageRange", "Unknown"))      # .get gives a default for a missing field
    print("Home library:", doc["homeLibrary"])
    print("Checkouts:", doc["totalCheckouts"])
    print("Renewals:", doc["totalRenewals"])


def update_checkouts():
    record_id = input("Patron record ID to update: ")
    new_total = input("New total checkouts: ")
    if not record_id.isdigit() or not new_total.isdigit():
        print("Please enter whole numbers only.")
        return
    result = mycol.update_one({"_id": int(record_id)},
                              {"$set": {"totalCheckouts": int(new_total)}})
    if result.matched_count == 0:
        print("No record has that ID.")
    else:
        print("Record", record_id, "now has", new_total, "checkouts.")


while True:
    print()
    print("SFILS Menu (MongoDB)")
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

myclient.close()
print("Goodbye.")
