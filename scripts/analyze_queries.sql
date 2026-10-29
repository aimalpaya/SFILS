USE sfils;
 
SELECT COUNT(*)            AS PatronRecords,
       SUM(TotalCheckouts) AS TotalCheckouts,
       SUM(TotalRenewals)  AS TotalRenewals
FROM   PATRON_RECORD;
 

SELECT   AgeRangeLabel,
         COUNT(*)                  AS PatronRecords,
         SUM(TotalCheckouts > 0)   AS UsedTheLibrary,
         SUM(TotalCheckouts > 1)   AS RepeatPatrons,
         SUM(TotalRenewals > 0)    AS Renewed
FROM     PATRON_RECORD LEFT JOIN AGE_RANGE
         ON PATRON_RECORD.AgeRangeID = AGE_RANGE.AgeRangeID
GROUP BY AgeRangeLabel
ORDER BY AgeRangeLabel;
 
SELECT   HomeLibraryDefinition AS Library,
         COUNT(*)              AS PatronRecords,
         SUM(TotalCheckouts)   AS Checkouts
FROM     PATRON_RECORD JOIN HOME_LIBRARY
         ON PATRON_RECORD.HomeLibraryCode = HOME_LIBRARY.HomeLibraryCode
GROUP BY HomeLibraryDefinition
ORDER BY Checkouts DESC
LIMIT 10;
 
SELECT   PatronTypeDefinition AS PatronType,
         COUNT(*)             AS PatronRecords,
         SUM(TotalCheckouts)  AS Checkouts
FROM     PATRON_RECORD JOIN PATRON_TYPE
         ON PATRON_RECORD.PatronTypeCode = PATRON_TYPE.PatronTypeCode
GROUP BY PatronTypeDefinition
ORDER BY PatronRecords DESC;

SELECT SUM(AgeRangeID IS NULL)             AS MissingAgeRange,
       SUM(CirculationActiveYear IS NULL)  AS MissingActiveYear,
       SUM(CirculationActiveMonth IS NULL) AS MissingActiveMonth
FROM   PATRON_RECORD;
 
