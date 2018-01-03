# Caisis Monthly Report #
=============================

Query Caisis database(s) based on metadata in config file (should be placed in the resources folder) to get high level updates on available data/ patient population snapshot. Output to individual excel workbooks with some simple graphs for visual representation of available data elements and mail workbooks with any error message(s). 

run from main_caisis_report_script.py

### /resources:
* config.json: contains DB connection details, seperate queries for cohort definition per disease group, as well as formatting variables for excel worksheets and report recipient emails
