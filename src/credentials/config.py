"""
CONFIGURATION FILE FOR GMAIL TO GOOGLE SHEETS AUTOMATION
========================================================

This file contains all the settings needed for the automation system.
Update these values according to your setup.
"""

import os

# ==================== PATHS CONFIGURATION ====================
# Base directory is where this config.py file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to your OAuth credentials file (download from Google Cloud Console)
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'credentials.json')

# Path where OAuth token will be stored (auto-generated after first run)
TOKEN_PATH = os.path.join(BASE_DIR, 'token.pickle')

# Path to store processed email IDs (prevents duplicate processing)
STATE_PATH = os.path.join(BASE_DIR, 'state', 'processed_emails.json')


# ==================== GOOGLE API SCOPES ====================
# These scopes define what permissions the app needs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read Gmail
    'https://www.googleapis.com/auth/spreadsheets'     # Write to Sheets
]


# ==================== GMAIL CONFIGURATION ====================
# Query to filter emails (Gmail search syntax)
# 'is:unread' = only unread emails
# You can modify this: 'is:unread label:inbox' or 'is:unread from:someone@example.com'
EMAIL_QUERY = 'is:unread'

# Maximum number of emails to process in one run
# Prevents processing too many emails at once
MAX_RESULTS = 50


# ==================== GOOGLE SHEETS CONFIGURATION ====================
# YOUR SPREADSHEET ID (from your URL)
# URL format: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
SPREADSHEET_ID = '1aGxu-mtYWQpETOoFnTMf1Q21-PP5mt8dlsDB-uIQ6XM'

# Name of the sheet/tab where emails will be logged
# You can change this to any existing sheet name in your spreadsheet
SHEET_NAME = 'Emails'

# Column headers for the sheet
# These will be created automatically on first run
HEADERS = ['From', 'Subject', 'Date', 'Content', 'Email ID']


# ==================== BONUS FEATURES (OPTIONAL) ====================
# Uncomment and modify these lines to enable bonus features:

# FILTER BY SUBJECT (Bonus feature)
# Only process emails containing specific text in subject
# SUBJECT_FILTER = 'Invoice'  # or 'Report', 'Newsletter', etc.

# TIME FILTER (Bonus feature)
# Only process emails from last X hours
# PROCESS_LAST_HOURS = 24

# EXCLUDE SENDERS (Bonus feature)
# Don't process emails from these senders
# EXCLUDE_SENDERS = ['no-reply@', 'noreply@', 'donotreply@']

# LOGGING LEVEL
# Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
# LOG_LEVEL = 'INFO'