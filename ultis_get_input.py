import os
import pandas as pd
import psycopg2
from config import (
    config,
    get_raw_data,
    trigger_github_workflow,
    insert_input_to_supabase,
    compare_data,
)

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
                SELECT date, keyword_phrase FROM keyword_input_sourcing 
                WHERE date = %s
            """,
            (current_time_gmt7.strftime("%Y-%m-%d"),),
        )
        # Fetch all results
        df = pd.DataFrame(cur.fetchall(), columns=["date", "keyword_phrase"])
        return df
    except Exception as e:
        print(f"Error fetching keywords from Supabase: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def get_data_from_supabase():
    response = supabase.table("keyword_input_sourcing").select("*").execute()
    if hasattr(response, "error") and response.error is not None:
        raise Exception("Failed to fetch data from Supabase")
    else:
        return pd.DataFrame(response.data)


while True:
    # Fetch raw data if needed
    supabase_data = get_data_from_supabase()
    if compare_data(get_raw_data(), supabase_data):
        print("New data found. Running workflow...")
        try:
            insert_input_to_supabase(get_raw_data())
        except Exception as e:
            print(f"Error upserting data to Supabase: {e}")
            continue

        # Fetch keyword from Supabase
        keywords = get_keyword_from_supabase()
        if keywords.empty:
            raise Exception("No keyword found for today's date")

        for _, row in keywords.iterrows():
            keyword = row["keyword_phrase"]
            trigger_github_workflow(keyword, GITHUB_TOKEN)
