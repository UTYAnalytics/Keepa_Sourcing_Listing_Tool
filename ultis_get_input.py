# Remember to close the browser
import os
import pandas as pd
import psycopg2
from config import config,get_raw_data,trigger_github_workflow,insert_input_to_supabase,compare_data

# Get Selenium configuration
chrome_options_list = config.get_selenium_config()

# Initialize Supabase client
supabase = config.supabase

db_config = config.get_database_config()
current_time_gmt7 = config.current_time_gmt7
GITHUB_TOKEN=os.getenv('MY_GITHUB_TOKEN')


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
        df = pd.DataFrame(cur.fetchall(), columns=["date","keyword_phrase"])
        return df
    except:
        return []
    finally:
        if conn:
            conn.close()

def get_data_from_supabase():
    response = supabase.table("keyword_input_sourcing").select("*").execute()
    if response.status_code == 200:
        return pd.DataFrame(response.data)
    else:
        raise Exception("Failed to fetch data from Supabase")
while True:      
    # Fetch raw data if needed
    supabase_data = get_data_from_supabase()
    if compare_data(get_raw_data(), supabase_data):
        print("New data found. Running workflow...")
        insert_input_to_supabase(get_raw_data())
        # Fetch keyword from Supabase
        keywords = get_keyword_from_supabase()
        if not keywords:
            raise Exception("No keyword found for today's date")
        for keyword in keywords:
            trigger_github_workflow(keyword, GITHUB_TOKEN)
