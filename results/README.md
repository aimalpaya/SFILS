# Findings

This folder contains our findings from this database project.

The findings include details about the library patrons. For example, how many from the age range 0 to 9 years used the library, how many of them were repeat patrons (can be found from total checkouts), how many renewed (can be found from total renewals).

Analyze Queries - creates multtiple tables to find values of libraries, totals, groups by age range, etc.

0 to 9 years:
Used library - 20148 patrons
Repeat patrons - 19143 patrons
Total Renewed - 17239 patrons

# Performance Metrics

This folder also contains the performance values.

Did we store the data in our database appropriately?

This is meant to be a more manageable database with multiple tables. We are not simply dumping the whole Excel sheet into one giant MySQL table.

Benchmark creates a normalized and denormalized(flat) table that finds the time in milliseconds for checkouts in library and per age range.

Checkouts per library: 
Normalized - 994.8 ms
Denormalized - 816.9 ms

Checkouts per age range:
Normalized - 816.9 ms
Denormalized - 643.3 ms
