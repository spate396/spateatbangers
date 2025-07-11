import streamlit as st
import pandas as pd
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Fix for ModuleNotFoundError by ensuring proper import paths
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ModuleNotFoundError:
    st.error("Missing Google API libraries. Please install dependencies using 'pip install -r requirements.txt'.")

# CONFIG
FROM_EMAIL = 'shivam.patel@eatbangers.com'
FROM_PASSWORD = 'your_app_password'  # App password from Gmail
CC_EMAIL = 'sales@eatbangers.com'
SHEET_ID = '1rg-gukQ7k0aIV6AtbOQEyJPwaXWBH_6T1KlCpSbewyA'
SHEET_RANGE = 'Sheet1!A:D'
CREDENTIALS_FILE = 'credentials.json'
PDF_ATTACHMENT = 'Bangers Product Presentation (Summer 2025).pdf'

@st.cache_data
def load_contacts(sheet_id, range_name):
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()
    values = result.get('values', [])
    return pd.DataFrame(values[1:], columns=values[0])

def build_email_body(name):
    return f"""Hey {name},

Hope you’re doing well!

I’m Shivam, with Bangers Snacks. Right now, we’re in 500+ stores and gearing up for a big launch with one of the top 5 convenience store chains in the U.S. We’d love to explore a potential partnership with you too.

Our potato chips aren’t your average snack—we bring bold, original flavors and even a caffeinated option, perfect for Gen Z consumers looking for something new. But what really sets us apart is our marketing reach—we’re already engaging 250M+ unique users through our Roblox games, generating more monthly views than the Super Bowl.

Our Gen-Z strategy rivals brands like Prime, Feastables, Lunchly, and JoyRide. We’re tapping into where the next generation actually spends their time, giving us a serious edge in driving demand.

I’ve attached our presentation for more context, and I’d love to hop on a quick call to see if there’s a good fit. Let me know your thoughts!

Best,  
Shivam Patel  
Bangers Snacks, Inc.  
E: shivam.patel@eatbangers.com  
M: 669-258-7074
"""

def send_email(name, to_email):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(FROM_EMAIL, FROM_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Cc'] = CC_EMAIL
    msg['Subject'] = "Let’s Connect – Gen Z Snacks That Actually Resonate"
    msg.attach(MIMEText(build_email_body(name), 'plain'))

    if os.path.exists(PDF_ATTACHMENT):
        with open(PDF_ATTACHMENT, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(PDF_ATTACHMENT))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(PDF_ATTACHMENT)}"'
        msg.attach(part)

    server.sendmail(FROM_EMAIL, [to_email, CC_EMAIL], msg.as_string())
    server.quit()

# Streamlit Interface
st.title("📧 Bangers Email Sender")

try:
    contacts = load_contacts(SHEET_ID, SHEET_RANGE)

    for i, row in contacts.iterrows():
        name = row.get("Contact Name", "there")
        email = row.get("Email", "")

        if not email or "@" not in email:
            continue

        with st.expander(f"{name} <{email}>"):
            if st.button(f"Send to {name}", key=i):
                try:
                    send_email(name, email)
                    st.success(f"✅ Email sent to {name}")
                except Exception as e:
                    st.error(f"❌ Failed to send: {e}")
except Exception as load_error:
    st.error(f"Failed to load contacts: {load_error}")