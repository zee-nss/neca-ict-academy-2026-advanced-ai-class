1

Write a Pandas script that does the following:

Number one: Load the messy CSV and print a complete inspection report. Shape of the data, data types of each column, and a count of missing values. This is your diagnostic step.

Number two: Clean all the issues you find. Remove duplicates. Fix the dates — handle the mixed formats using pd.to_datetime with errors='coerce'. Fill missing quantities with the median. Mark missing regions as 'Unknown.' Replace zero and negative prices using product-specific medians. Standardize product names — strip spaces, apply consistent capitalization.

Number three: Add at least one calculated column. Could be total sale amount, could be extracting the month from the date, could be something else useful.

Number four: Create one aggregation summary — like total sales by region, or average quantity by product. Something that would normally be a pivot table in Excel.

Number five: Save the cleaned data as both CSV and Excel files.

Number six — most importantly: Print a before-and-after summary. Something like: 'Fixed 5 duplicate rows, 12 missing quantities, 8 invalid dates, 15 inconsistent product names.' Show what your script accomplished.

The key requirement: Your cleaning rules must be AUTOMATIC. No hardcoding specific values you saw. No 'I looked at the data and decided.' Write rules that would work on a new dataset next week with different values.

Submit your Python file before tomorrow's video. If you get stuck, the community channel is open."

2
