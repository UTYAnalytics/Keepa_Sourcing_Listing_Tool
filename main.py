# Remember to close the browser
import tempfile
from selenium import webdriver
import os
import pandas as pd
import psycopg2
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
from config import config
from keepa_API import fetch_keepa_asins
from keeepa_viewer import keepa_viewer
import sys


display = Display(visible=0, size=(800, 800))
display.start()

chromedriver_autoinstaller.install()

# Get Selenium configuration
chrome_options_list = config.get_selenium_config()

# Initialize Supabase client
supabase = config.supabase

db_config = config.get_database_config()
current_time_gmt7 = config.current_time_gmt7
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")


# Your existing function to get the keyword from Supabase
def get_keyword_from_supabase():
    conn = None
    try:
        # Connect to your database
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
        )
        cur = conn.cursor()
        # Execute a query
        cur.execute(
            """
                SELECT date,keyword_phrase FROM keyword_input_sourcing a where date=%s
                """,
            (current_time_gmt7.strftime("%Y-%m-%d"),),
        )
        # Fetch all results
        df = pd.DataFrame(cur.fetchall(), columns=["date", "keyword_phrase"])
        return df
    except:
        return []
    finally:
        if conn:
            conn.close()


# Create a temporary directory for downloads
with tempfile.TemporaryDirectory() as download_dir:
    # Chrome options
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    for option in chrome_options_list:
        chrome_options.add_argument(option)

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        key = os.getenv(
            "KEEPA_API_KEY"
        )  # Ensure the API key is stored in an environment variable
        print(sys.argv[1])
        keyword_list = sys.argv[1]
        domain = 1
        selection = {
            "title": keyword_list,
            "rootCategory": 16310101,
            "sort": [["current_SALES", "asc"]],
            "productType": [0, 1, 2],
            "page": 0,
            "perPage": 5000,
        }

        output_file_path = f"{download_dir}/all_asins.txt"
        fetch_keepa_asins(key, domain, selection, output_file_path)
        keepa_viewer(driver, output_file_path, download_dir)

    finally:
        if driver:
            driver.quit()
