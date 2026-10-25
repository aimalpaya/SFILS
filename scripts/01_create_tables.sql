/* *** SFILS-CREATE-SCHEMA *** */
-- San Francisco Integrated Library System (SFILS)
-- Creates the schema and the five normalized tables.
-- Run this script first, before the data-loading script.

CREATE SCHEMA IF NOT EXISTS sfils;
USE sfils;

/* *** SFILS-DROP-TABLES *** */
-- Drop child tables before parent tables so foreign keys do not block the drop.
DROP TABLE IF EXISTS PATRON_RECORD;
DROP TABLE IF EXISTS NOTIFICATION_PREFERENCE;
DROP TABLE IF EXISTS HOME_LIBRARY;
DROP TABLE IF EXISTS AGE_RANGE;
DROP TABLE IF EXISTS PATRON_TYPE;

/* *** SFILS-CREATE-PATRON-TYPE *** */
-- Source: 'Patron Type Code' -> 'Patron Type Definition' (18 codes, 1:1 with definitions)
CREATE TABLE PATRON_TYPE (
    PatronTypeCode        Int          NOT NULL,
    PatronTypeDefinition  VarChar(30)  NOT NULL,
    CONSTRAINT PATRON_TYPE_PK PRIMARY KEY (PatronTypeCode)
);

/* *** SFILS-CREATE-AGE-RANGE *** */
-- Source: 'Age Range' (10 distinct labels). Surrogate key because the source has no age code.
CREATE TABLE AGE_RANGE (
    AgeRangeID     Int          NOT NULL AUTO_INCREMENT,
    AgeRangeLabel  VarChar(30)  NOT NULL UNIQUE,
    CONSTRAINT AGE_RANGE_PK PRIMARY KEY (AgeRangeID)
);

/* *** SFILS-CREATE-HOME-LIBRARY *** */
-- Source: 'Home Library Code' -> 'Home Library Definition'.
-- 67 codes map to only 30 names, so the CODE is the key (several codes can share one name).
CREATE TABLE HOME_LIBRARY (
    HomeLibraryCode        VarChar(10)  NOT NULL,
    HomeLibraryDefinition  VarChar(50)  NOT NULL,
    CONSTRAINT HOME_LIBRARY_PK PRIMARY KEY (HomeLibraryCode)
);

/* *** SFILS-CREATE-NOTIFICATION-PREFERENCE *** */
-- Source: 'Notification Preference Code' -> 'Notification Code Definition'.
-- The code '-' has no definition in the source; the loader labels it 'Not specified'.
CREATE TABLE NOTIFICATION_PREFERENCE (
    NotificationCode        Char(1)      NOT NULL,
    NotificationDefinition  VarChar(30)  NOT NULL,
    CONSTRAINT NOTIFICATION_PREFERENCE_PK PRIMARY KEY (NotificationCode)
);

/* *** SFILS-CREATE-PATRON-RECORD *** */
-- One row per anonymized patron record in the source file (the source has no patron ID).
-- AgeRangeID, HomeLibraryCode, CirculationActiveMonth and CirculationActiveYear
-- are nullable because the source contains missing values for them.
CREATE TABLE PATRON_RECORD (
    PatronRecordID          Int          NOT NULL AUTO_INCREMENT,
    PatronTypeCode          Int          NOT NULL,
    AgeRangeID              Int          NULL,
    HomeLibraryCode         VarChar(10)  NULL,
    NotificationCode        Char(1)      NOT NULL,
    TotalCheckouts          Int          NOT NULL DEFAULT 0,
    TotalRenewals           Int          NOT NULL DEFAULT 0,
    CirculationActiveMonth  VarChar(12)  NULL,
    CirculationActiveYear   Int          NULL,
    ProvidedEmail           Boolean      NOT NULL,
    WithinSFCounty          Boolean      NOT NULL,
    YearRegistered          Int          NOT NULL,
    CONSTRAINT PATRON_RECORD_PK PRIMARY KEY (PatronRecordID),
    CONSTRAINT PR_PATRON_TYPE_FK FOREIGN KEY (PatronTypeCode)
        REFERENCES PATRON_TYPE (PatronTypeCode)
        ON UPDATE CASCADE,
    CONSTRAINT PR_AGE_RANGE_FK FOREIGN KEY (AgeRangeID)
        REFERENCES AGE_RANGE (AgeRangeID)
        ON UPDATE CASCADE,
    CONSTRAINT PR_HOME_LIBRARY_FK FOREIGN KEY (HomeLibraryCode)
        REFERENCES HOME_LIBRARY (HomeLibraryCode)
        ON UPDATE CASCADE,
    CONSTRAINT PR_NOTIFICATION_FK FOREIGN KEY (NotificationCode)
        REFERENCES NOTIFICATION_PREFERENCE (NotificationCode)
        ON UPDATE CASCADE
);

/* *** SFILS-VERIFY *** */
SHOW TABLES;
