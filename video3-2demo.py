import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --------------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------------

# Define the scope — what we're allowed to do
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Authenticate using the service account JSON key
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'service_account.json', 
    scope
)

gc = gspread.authorize(credentials)

print("Authenticated successfully")
print("Connected to Google Sheets")


# --------------------------------------------------------
# READING FROM GOOGLE SHEETS
# --------------------------------------------------------

def read_sheet(sheet_url, worksheet_name='Sheet1'):
    """
    Read any Google Sheet into a Pandas DataFrame.
    You need to have shared the sheet with your service account.
    """
    
    # Open the spreadsheet by URL
    spreadsheet = gc.open_by_url(sheet_url)
    
    # Get the specific worksheet
    worksheet = spreadsheet.worksheet(worksheet_name)
    
    # Get all data as a list of dictionaries
    data = worksheet.get_all_records()
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    print("Read from:", spreadsheet.title)
    print("Worksheet:", worksheet_name)
    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    
    return df, spreadsheet

# --------------------------------------------------------
# WRITING TO GOOGLE SHEETS
# --------------------------------------------------------

def write_to_sheet(spreadsheet, df, worksheet_name='Automated Output'):
    """
    Write a DataFrame to Google Sheets.
    Creates a new worksheet or overwrites an existing one.
    """
    
    # Try to get existing worksheet
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        worksheet.clear()
        print("Clearing existing worksheet:", worksheet_name)
    except:
        # Create new worksheet if it doesn't exist
        worksheet = spreadsheet.add_worksheet(
            worksheet_name, 
            rows=len(df) + 1, 
            cols=len(df.columns)
        )
        print("Creating new worksheet:", worksheet_name)
    
    # Convert DataFrame to list of lists
    # First row is the headers
    data_to_write = [df.columns.tolist()] + df.values.tolist()
    
    # Write everything at once
    worksheet.update(data_to_write)
    
    print("Written", len(df), "rows to", worksheet_name)
    return worksheet
# --------------------------------------------------------
# TEST: READ FROM A GOOGLE SHEET
# --------------------------------------------------------

# CHANGE THIS to your sheet URL
SHEET_URL = 'https://docs.google.com/spreadsheets/d/18PtcEuVvtd2kFBGeefyXHeayUsKbODBxVII24zO9xI8/edit?usp=sharing'

print("TESTING READ FROM GOOGLE SHEETS")
print("=" * 50)

df_leads, sheet = read_sheet(SHEET_URL, 'Leads')

print()
print("Data from sheet:")
print(df_leads)

# --------------------------------------------------------
# REAL AUTOMATION: ENRICH LEADS FROM GOOGLE SHEETS
# --------------------------------------------------------

def calculate_lead_score(lead):
    """
    Simple rule-based lead scoring.
    Replace with machine learning in Month 2.
    """
    score = 5  # Base score
    
    # Higher score for high-value industries
    high_value = ['Technology', 'Finance', 'Healthcare']
    if lead.get('Industry') in high_value:
        score += 2
    
    # Higher score for certain statuses
    if lead.get('Status') == 'Qualified':
        score += 2
    elif lead.get('Status') == 'Contacted':
        score += 1
    
    return min(score, 10)


def enrich_leads_sheet(sheet_url):
    """
    Read leads from Google Sheets, enrich with scoring,
    write results back to a new worksheet.
    """
    print("STARTING LEAD ENRICHMENT")
    print("=" * 50)
    
    # Step 1: Read current leads
    print()
    print("Reading leads from Google Sheets...")
    df_leads, spreadsheet = read_sheet(sheet_url, 'Leads')
    
    # Step 2: Add enrichment columns
    print()
    print("Enriching leads...")
    
    # Add a source note
    df_leads['Source_Note'] = 'Enriched by automation on ' + pd.Timestamp.now().strftime('%Y-%m-%d')
    
    # Calculate priority score for each lead
    df_leads['Priority_Score'] = df_leads.apply(calculate_lead_score, axis=1)
    
    # Categorize priority
    def categorize_priority(score):
        if score >= 8:
            return 'High'
        elif score >= 6:
            return 'Medium'
        else:
            return 'Low'
    
    df_leads['Priority_Category'] = df_leads['Priority_Score'].apply(categorize_priority)
    
    print("Added columns: Priority_Score, Priority_Category, Source_Note")
    
    # Step 3: Write enriched data to new sheet
    print()
    print("Writing enriched data back to Google Sheets...")
    write_to_sheet(spreadsheet, df_leads, 'Enriched Leads')
    
    # Step 4: Create a summary sheet
    print()
    print("Creating summary sheet...")
    
    summary = df_leads.groupby('Priority_Category').agg({
        'Company': 'count',
        'Priority_Score': 'mean'
    }).round(1)
    summary.columns = ['Lead Count', 'Average Score']
    
    write_to_sheet(spreadsheet, summary.reset_index(), 'Lead Summary')
    
    # Step 5: Print completion
    print()
    print("=" * 50)
    print("ENRICHMENT COMPLETE")
    print("Total leads processed:", len(df_leads))
    
    high_priority = len(df_leads[df_leads['Priority_Score'] >= 8])
    print("High priority leads:", high_priority)
    
    return df_leads

# --------------------------------------------------------
# RUN THE ENRICHMENT
# --------------------------------------------------------

print()
print("RUNNING LEAD ENRICHMENT AUTOMATION")
print("=" * 50)

enriched = enrich_leads_sheet(SHEET_URL)

print()
print("Sample of enriched leads:")
print(enriched[['Company', 'Industry', 'Status', 'Priority_Score', 'Priority_Category']])


