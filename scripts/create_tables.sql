USE sfils;

DROP TABLE IF EXISTS PATRON_RECORD;
DROP TABLE IF EXISTS NOTIFICATION_PREFERENCE;
DROP TABLE IF EXISTS HOME_LIBRARY;
DROP TABLE IF EXISTS AGE_RANGE;
DROP TABLE IF EXISTS PATRON_TYPE;

CREATE TABLE PATRON_TYPE (
    PatronTypeCode        Int          NOT NULL,
    PatronTypeDefinition  VarChar(50)  NOT NULL,
    CONSTRAINT PATRON_TYPE_PK PRIMARY KEY (PatronTypeCode)
);

CREATE TABLE AGE_RANGE (
    AgeRangeID     Int          NOT NULL AUTO_INCREMENT,
    AgeRangeLabel  VarChar(30)  NOT NULL UNIQUE,
    CONSTRAINT AGE_RANGE_PK PRIMARY KEY (AgeRangeID)
);

CREATE TABLE HOME_LIBRARY (
    HomeLibraryCode        VarChar(10)  NOT NULL,
    HomeLibraryDefinition  VarChar(100)  NOT NULL,
    CONSTRAINT HOME_LIBRARY_PK PRIMARY KEY (HomeLibraryCode)
);

CREATE TABLE NOTIFICATION_PREFERENCE (
    NotificationCode        Char(1)      NOT NULL,
    NotificationDefinition  VarChar(50)  NOT NULL,
    CONSTRAINT NOTIFICATION_PREFERENCE_PK PRIMARY KEY (NotificationCode)
);

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
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT PR_AGE_RANGE_FK FOREIGN KEY (AgeRangeID)
        REFERENCES AGE_RANGE (AgeRangeID)
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT PR_HOME_LIBRARY_FK FOREIGN KEY (HomeLibraryCode)
        REFERENCES HOME_LIBRARY (HomeLibraryCode)
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT PR_NOTIFICATION_FK FOREIGN KEY (NotificationCode)
        REFERENCES NOTIFICATION_PREFERENCE (NotificationCode)
        ON UPDATE CASCADE
        ON DELETE NO ACTION
);

SHOW TABLES;
