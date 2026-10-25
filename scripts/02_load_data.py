"""
02_load_data.py -- Load the SFPL Library Usage file into the sfils database.

Usage:
    python 02_load_data.py "C:/path/to/SFPL_DataSF_library-usage_Jan 2023.xlsx"

Connection settings come from environment variables, so no password is ever
stored in the repository:
    SFILS_DB_HOST      default: localhost
    SFILS_DB_PORT      default: 3306
    SFILS_DB_USER      default: root
    SFILS_DB_PASSWORD  default: you are prompted for it
    SFILS_DB_NAME      default: sfils

Run 01_create_tables.sql first. This script expects the tables to be empty.
"""
import argparse
import getpass
import os
import re
import sys
import time

import mysql.connector
import numpy as np
import pandas as pd

BATCH_SIZE = 10_000

EXPECTED_COLUMNS = [
    "Patron Type Code", "Patron Type Definition", "Total Checkouts",
    "Total Renewals", "Age Range", "Home Library Code",
    "Home Library Definition", "Circulation Active Month",
    "Circulation Active Year", "Notification Preference Code",
    "Notification Code Definition", "Provided Email Address",
    "Within San Francisco County", "Year Patron Registered",
]

TEXT_COLUMNS = [
    "Patron Type Definition", "Age Range", "Home Library Code",
    "Home Library Definition", "Circulation Active Month",
    "Notification Preference Code", "Notification Code Definition",
]


# ----------------------------------------------------------------------
# Reading and cleaning
# ----------------------------------------------------------------------
def read_source(path):
    print(f"Reading {path} (this can take a minute)...")
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    # The source headers contain hidden newlines, e.g. 'Age Range\n'.
    df.columns = df.columns.str.split("\n").str[0].str.strip()
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        sys.exit(f"Missing expected columns: {missing}\nFound: {df.columns.tolist()}")
    return df


def to_bool(value):
    """Convert true/false style values to a Python bool (or None if missing)."""
    if pd.isna(value):
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    text = str(value).strip().lower()
    if text in ("true", "t", "yes", "y", "1"):
        return True
    if text in ("false", "f", "no", "n", "0"):
        return False
    raise ValueError(f"Cannot interpret {value!r} as a boolean")


def clean(df):
    df = df.copy()

    # Strip whitespace from text columns; blank strings become missing values.
    for col in TEXT_COLUMNS:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

    # Cleaning decisions (documented in docs/):
    #  - the 2 rows with no home library code become 'none' (source says 'Unknown')
    #  - notification code '-' has no definition in the source -> 'Not specified'
    df["Home Library Code"] = df["Home Library Code"].fillna("none")
    df["Home Library Definition"] = df["Home Library Definition"].fillna("Unknown")
    df["Notification Code Definition"] = df["Notification Code Definition"].fillna("Not specified")

    # Numbers
    df["Patron Type Code"] = pd.to_numeric(df["Patron Type Code"]).astype("int64")
    df["Total Checkouts"] = pd.to_numeric(df["Total Checkouts"]).astype("int64")
    df["Total Renewals"] = pd.to_numeric(df["Total Renewals"]).astype("int64")
    df["Year Patron Registered"] = pd.to_numeric(df["Year Patron Registered"]).astype("int64")
    # Missing years stay missing (NULL in the database).
    df["Circulation Active Year"] = pd.to_numeric(
        df["Circulation Active Year"], errors="coerce").astype("Int64")

    # Booleans
    df["Provided Email Address"] = df["Provided Email Address"].map(to_bool)
    df["Within San Francisco County"] = df["Within San Francisco County"].map(to_bool)
    return df


def py(value):
    """Convert pandas/numpy values to plain Python values (NA -> None)."""
    if value is None or value is pd.NA:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, np.generic):
        return value.item()
    return value


def build_lookup(df, code_col, def_col, name):
    """Distinct (code, definition) pairs; warn if a code has several definitions."""
    pairs = df[[code_col, def_col]].drop_duplicates()
    clashes = pairs[pairs.duplicated(code_col, keep=False)]
    if not clashes.empty:
        print(f"WARNING: {name}: some codes have more than one definition; keeping the first.")
        print(clashes.to_string())
    pairs = pairs.drop_duplicates(code_col).sort_values(code_col)
    return [(py(c), py(d)) for c, d in zip(pairs[code_col], pairs[def_col])]


def age_sort_key(label):
    """Order labels like '0 to 9 years' ... '75 years and over' by their first number."""
    match = re.search(r"\d+", label)
    return int(match.group()) if match else 10**6


# ----------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------
def connect():
    password = os.environ.get("SFILS_DB_PASSWORD") or getpass.getpass("MySQL password: ")
    return mysql.connector.connect(
        host=os.environ.get("SFILS_DB_HOST", "localhost"),
        port=int(os.environ.get("SFILS_DB_PORT", "3306")),
        user=os.environ.get("SFILS_DB_USER", "root"),
        password=password,
        database=os.environ.get("SFILS_DB_NAME", "sfils"),
    )


def main():
    parser = argparse.ArgumentParser(description="Load SFPL library usage data into MySQL.")
    parser.add_argument("data_file", help="path to the .xlsx (or .csv) data file")
    args = parser.parse_args()

    started = time.perf_counter()
    df = clean(read_source(args.data_file))
    total_rows = len(df)
    print(f"Read and cleaned {total_rows:,} rows in {time.perf_counter() - started:.1f} s")

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM PATRON_RECORD")
    if cur.fetchone()[0] > 0:
        sys.exit("PATRON_RECORD already has rows. Re-run 01_create_tables.sql to start clean.")

    # --- lookup tables -------------------------------------------------
    patron_types = build_lookup(df, "Patron Type Code", "Patron Type Definition", "PATRON_TYPE")
    cur.executemany("INSERT INTO PATRON_TYPE (PatronTypeCode, PatronTypeDefinition) VALUES (%s, %s)",
                    patron_types)

    libraries = build_lookup(df, "Home Library Code", "Home Library Definition", "HOME_LIBRARY")
    cur.executemany("INSERT INTO HOME_LIBRARY (HomeLibraryCode, HomeLibraryDefinition) VALUES (%s, %s)",
                    libraries)

    notices = build_lookup(df, "Notification Preference Code", "Notification Code Definition",
                           "NOTIFICATION_PREFERENCE")
    cur.executemany("INSERT INTO NOTIFICATION_PREFERENCE (NotificationCode, NotificationDefinition) VALUES (%s, %s)",
                    notices)

    age_labels = sorted(df["Age Range"].dropna().unique(), key=age_sort_key)
    cur.executemany("INSERT INTO AGE_RANGE (AgeRangeLabel) VALUES (%s)", [(a,) for a in age_labels])
    conn.commit()

    cur.execute("SELECT AgeRangeLabel, AgeRangeID FROM AGE_RANGE")
    age_ids = dict(cur.fetchall())
    print(f"Lookup tables loaded: {len(patron_types)} patron types, {len(age_labels)} age ranges, "
          f"{len(libraries)} home libraries, {len(notices)} notification preferences")

    # --- main table ----------------------------------------------------
    df["AgeRangeID"] = df["Age Range"].map(age_ids)
    columns = [
        "Patron Type Code", "AgeRangeID", "Home Library Code",
        "Notification Preference Code", "Total Checkouts", "Total Renewals",
        "Circulation Active Month", "Circulation Active Year",
        "Provided Email Address", "Within San Francisco County",
        "Year Patron Registered",
    ]
    column_values = [[py(v) for v in df[c].tolist()] for c in columns]
    rows = list(zip(*column_values))

    sql = ("INSERT INTO PATRON_RECORD (PatronTypeCode, AgeRangeID, HomeLibraryCode, "
           "NotificationCode, TotalCheckouts, TotalRenewals, CirculationActiveMonth, "
           "CirculationActiveYear, ProvidedEmail, WithinSFCounty, YearRegistered) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    load_start = time.perf_counter()
    for start in range(0, total_rows, BATCH_SIZE):
        cur.executemany(sql, rows[start:start + BATCH_SIZE])
        conn.commit()
        done = min(start + BATCH_SIZE, total_rows)
        print(f"  inserted {done:,} / {total_rows:,}", end="\r")
    print()
    load_seconds = time.perf_counter() - load_start

    # --- verification ----------------------------------------------------
    cur.execute("SELECT COUNT(*) FROM PATRON_RECORD")
    loaded = cur.fetchone()[0]
    print(f"Rows in file: {total_rows:,} | rows in PATRON_RECORD: {loaded:,}")
    print("Row counts match." if loaded == total_rows else "WARNING: row counts differ!")
    print(f"PATRON_RECORD load took {load_seconds:.1f} s; whole script {time.perf_counter() - started:.1f} s")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
