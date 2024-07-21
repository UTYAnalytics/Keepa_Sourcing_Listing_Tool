import toml
from supabase import create_client
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import imaplib
import email
import re
import pandas as pd
from datetime import datetime, timedelta
import glob
import os
import unicodedata
import json
import requests

class Config:
    def __init__(self, config_path="config.toml"):
        self.config = toml.load(config_path)
        self.supabase = self.init_supabase()
        self.current_time_gmt7 = self.calculate_gmt7_time()
        # self.MY_GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")

    def get_supabase_config(self):
        supabase_config = self.config.get("supabase", {})
        return supabase_config["url"], supabase_config["key"]

    def get_database_config(self):
        return self.config.get("database", {})

    def get_timezone_offset(self):
        timezone_config = self.config.get("timezone", {})
        return timezone_config.get("offset_hours", 0)

    def init_supabase(self):
        supabase_url, supabase_key = self.get_supabase_config()
        return create_client(supabase_url, supabase_key)

    def calculate_gmt7_time(self):
        timezone_offset_hours = self.get_timezone_offset()
        current_utc_time = datetime.utcnow()
        gmt7_offset = timedelta(hours=timezone_offset_hours)
        return current_utc_time + gmt7_offset

    def get_selenium_config(self):
        selenium_config = self.config.get("selenium", {})
        return selenium_config.get("chrome_options", [])

    def get_keepa(self):
        keepa_config = self.config.get("keepa", {})
        return keepa_config["username"], keepa_config["password"]

    def get_otp_from_email(self):
        get_otp_from_email_config = self.config.get("Gmai", {})
        return (
            get_otp_from_email_config["server"],
            get_otp_from_email_config["email_address"],
            get_otp_from_email_config["email_password"],
            get_otp_from_email_config["subject_filter"],
        )
    def get_github_config(self):
        github_config = self.config.get("github", {})
        return (
            github_config["repo"],
            github_config["workflow_id"],
            github_config["branch"],
        )


def wait_for_value_greater_than_zero(driver, locator):
    # Wait for the element to be present
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    # Continuously check the value until it's greater than 0
    while True:
        # Get the current value of the element
        current_value = float(element.text)  # Assuming the value is numeric

        if current_value > 0:
            break  # Exit the loop if the condition is met

        # Wait for a short interval before checking again
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element(locator, str(current_value))
        )


def get_otp_from_email(server, email_address, email_password, subject_filter):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email_address, email_password)
    mail.select("inbox")

    status, data = mail.search(None, '(SUBJECT "{}")'.format(subject_filter))
    mail_ids = data[0].split()

    latest_email_id = mail_ids[-1]
    status, data = mail.fetch(latest_email_id, "(RFC822)")

    raw_email = data[0][1].decode("utf-8")
    email_message = email.message_from_bytes(data[0][1])

    otp_pattern = re.compile(r"\b\d{6}\b")

    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            if "text/plain" in content_type or "text/html" in content_type:
                email_content = part.get_payload(decode=True).decode()
                match = otp_pattern.search(email_content)
                if match:
                    return match.group(0)
    else:
        email_content = email_message.get_payload(decode=True).decode()
        match = otp_pattern.search(email_content)
        if match:
            return match.group(0)

    return None

def get_newest_file(directory):
            files = glob.glob(os.path.join(directory, "*"))
            if not files:  # Check if the files list is empty
                return None
            newest_file = max(files, key=os.path.getmtime)
            return newest_file

def clean_data(value):
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, str) and value.lower() == "nan":
        return None
    if isinstance(value, (int, float)):
        return value
    return str(value)

# Helper function to remove $ and convert to float
def clean_currency(value):
    try:
        if pd.isna(value) or value == "-":
            return 0
        if isinstance(value, str):
            return float(value.replace("$", "").replace(",", "").strip())
        return float(value)
    except:
        return 0.00

# Helper function to remove % and convert to percentage
def clean_percentage(value):
    try:
        if pd.isna(value) or value == "-":
            return 0
        if isinstance(value, str):
            return float(value.replace("%", "").strip()) / 100
        return float(value)
    except:
        return 0.00

def format_header(header):
            # Convert to lowercase
            header = header.lower()
            # Replace spaces with underscores
            header = header.replace(" ", "_")
            # Remove Vietnamese characters by decomposing and keeping only ASCII
            header = (
                unicodedata.normalize("NFKD", header)
                .encode("ASCII", "ignore")
                .decode("ASCII")
            )
            return header

def convert_google_sheet_url(url: str = None) -> str:
    """Function to convert the url to get dataframe from pandas"""
    # Regular expression to match and capture the necessary part of the URL
    pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?"
    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = (
        lambda m: f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?"
        + (f"gid={m.group(3)}&" if m.group(3) else "")
        + "format=csv"
    )
    # Replace using regex
    new_url = re.sub(pattern, replacement, url)
    return new_url


def get_raw_data(
    path: str = None,
) -> pd.DataFrame:  # TODO: this will be changed to getting from Supabase
    """This function to convert the URL of the Google Sheet to a DataFrame

    Args:
        path (str): PATH of the Google Sheet. Defaults to None.

    Returns:
        pd.DataFrame: Output DataFrame.
    """
    url = convert_google_sheet_url(path)
    data = pd.read_csv(url)
    return data

def convert_google_sheet_url(url: str = None) -> str:
    """Function to convert the url to get dataframe from pandas
    """
    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
    # Replace using regex
    new_url = re.sub(pattern, replacement, url)
    return new_url

def get_raw_data(path=Config().config["data"]["input"]["path"]) -> pd.DataFrame: #TODO: this will be changed to getting from Supabase
    """This function to convert the URL of the Google Sheet to a DataFrame

    Args:
        path (str): PATH of the Google Sheet. Defaults to None.

    Returns:
        pd.DataFrame: Output DataFrame.
    """
    
    url = convert_google_sheet_url(path)
    data = pd.read_csv(url)
    return data

def compare_data(google_sheet_data: pd.DataFrame, supabase_data: pd.DataFrame) -> bool:
    """Compare Google Sheet data with Supabase data.

    Args:
        google_sheet_data (pd.DataFrame): Data from Google Sheet.
        supabase_data (pd.DataFrame): Data from Supabase.

    Returns:
        bool: True if there is new data in the Google Sheet, False otherwise.
    """
    if google_sheet_data.equals(supabase_data):
        return False
    else:
        return True

def insert_input_to_supabase(data):
     # Convert DataFrame to dictionary records
    data_records = data.to_dict(orient='records')
    # Insert records into Supabase table
    # response = Config().supabase.table(table_name).upsert(data_records).execute()
    try:
        response = Config().supabase.table("keyword_input_sourcing").upsert(data_records).execute()
        if hasattr(response, "error") and response.error is not None:
            raise Exception(f"Error inserting rows: {response.error}")
        print(f"Row inserted successfully")
    except Exception as e:
        print(f"Error upserting batch: {e}")

def trigger_github_workflow(keywords, GITHUB_TOKEN):
    config = Config()
    GITHUB_REPO, WORKFLOW_ID, BRANCH = config.get_github_config()

    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{WORKFLOW_ID}/dispatches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    data = {"ref": BRANCH, "inputs": {"keyword_list": json.dumps(keywords)}}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 204:
        print("Workflow triggered successfully")
    else:
        print(f"Failed to trigger workflow: {response.status_code}, {response.text}")

# Initialize the configuration
config = Config()
