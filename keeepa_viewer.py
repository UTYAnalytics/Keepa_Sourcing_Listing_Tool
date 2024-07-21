# Remember to close the browser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from config import (
    config,
    get_otp_from_email,
    clean_data,
    get_newest_file,
    clean_currency,
    clean_percentage,
    format_header,
)
import math

# import keepa_API as keepa_API

# Initialize Supabase client
supabase = config.supabase

db_config = config.get_database_config()

username, password = config.get_keepa()
server, email_address, email_password, subject_filter = config.get_otp_from_email()

# Get timezone offset and calculate current time in GMT+7
current_time_gmt7 = config.current_time_gmt7


def keepa_viewer(driver, output_file_path, download_dir):
    # Open Keepa
    driver.get("https://keepa.com/#!")

    wait = WebDriverWait(driver, 20)
    # Login process
    try:
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="panelUserRegisterLogin"]'))
        )
        login_button.click()

        username_field = wait.until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(username)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
        # This is a hypothetical CSS selector targeting the close button inside a specific parent
        # Adjust the selector based on the actual structure of your HTML
        close_button_selector = "#shareChartOverlay-close .fa-times-circle"
    except:
        print("Error during login Keepa")

    try:
        # Wait for the popup close button to be clickable
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, close_button_selector))
        )

        # Find the close button using the CSS selector and click it
        close_button = driver.find_element(By.CSS_SELECTOR, close_button_selector)
        close_button.click()
    except:
        print(
            "The close button was not found or the popup did not appear within the timeout period."
        )

    try:
        otp = get_otp_from_email(server, email_address, email_password, subject_filter)
        if otp:
            otp_field = driver.find_element(By.ID, "otp")
            otp_field.send_keys(otp)
            otp_field.send_keys(Keys.RETURN)
            time.sleep(5)
    except:
        print("OTP field not found. Check the HTML or the timing.")

    # Navigate to the product_viewer
    try:
        data_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="topMenu"]/li[4]/a/span'))
        )
        data_button.click()
        time.sleep(2)
        productviewer_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="subPanel"]/ul[3]/li[2]/a'))
        )
        productviewer_button.click()

        # ListAsin_field = wait.until(
        #     EC.visibility_of_element_located((By.ID, "importInputAsin"))
        # )
        # ListAsin_field.send_keys(asin_string)

        # Wait until the file input element is present
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "importInputFile"))
        )

        # Specify the file path you want to upload
        file_path = output_file_path

        # Send the file path to the file input element
        file_input.send_keys(file_path)
        time.sleep(2)
        Loadlist_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="importSubmit"]'))
        )
        Loadlist_button.click()
        # Wait for the progress to reach 100%
        print("wait for processing...")
        while True:
            try:
                progress_text = driver.find_element(
                    By.CSS_SELECTOR, ".loadingProgress .bigAndBold"
                ).text
                print(progress_text)
                if not progress_text:
                    break
            except:
                time.sleep(2)

        # Logic to handle the presence of a specific popup
        try:
            # Wait for a certain amount of time for the popup to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "popup3"))
            )
            raise Exception("Popup detected, skipping to next retailer")
        except:
            try:
                # Try to find the close button of the popup
                close_button = driver.find_element(By.ID, "shareChartOverlay-close4")
                # If found, click it to close the popup
                close_button.click()
                print("Popup was found and closed.")
            except:
                # If the close button is not found, the popup is not displayed
                print("Popup not found; continuing with the script.")

            print("export")
            export_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="grid-tools-viewer"]/div[1]/span[3]/span',
                    )
                )
            )
            export_button.click()
            time.sleep(2)
            final_download_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="exportSubmit"]'))
            )
            final_download_button.click()
            time.sleep(2)
            driver.quit()

        file_path = download_dir

        newest_file_path = get_newest_file(file_path)
        # # Get the current UTC time
        # current_utc_time = datetime.utcnow()

        # # Calculate the time difference for GMT+7
        # gmt7_offset = timedelta(hours=7)

        # # Get the current date and time in GMT+7
        # current_time_gmt7 = current_utc_time + gmt7_offset
        if newest_file_path:
            data = pd.read_csv(newest_file_path)
            data["sys_run_date"] = current_time_gmt7.strftime("%Y-%m-%d")
            # Proceed with the database insertion
        else:
            print("No files found in the specified directory.")

        # Extract the header row
        headers = [
            "Locale",
            "Image_URLs",
            "Title",
            "Sales_Rank_Current",
            "Sales_Rank_90_Days_Avg",
            "Sales_Rank_90_Days_Drop_Percent",
            "Sales_Rank_Drops_Last_90_Days",
            "Sales_Rank_Reference",
            "Sales_Rank_Subcategory_Sales_Ranks",
            "Bought_Past_Month",
            "_90_Days_Change_Percent_Monthly_Sold",
            "Reviews_Rating",
            "Reviews_Review_Count",
            "Reviews_Review_Count_90_Days_Drop_Percent",
            "Ratings_Format_Specific",
            "Review_Count_Format_Specific",
            "Last_Price_Change",
            "Buy_Box_Current_Price",
            "Buy_Box_90_Days_Avg_Price",
            "Buy_Box_90_Days_Drop_Percent",
            "Buy_Box_Stock",
            "Buy_Box_90_Days_OOS_Percent",
            "Buy_Box_Seller",
            "Buy_Box_Percent_Amazon_90_Days",
            "Buy_Box_Percent_Top_Seller_90_Days",
            "Buy_Box_Winner_Count_90_Days",
            "Buy_Box_Is_FBA",
            "Buy_Box_Unqualified",
            "Amazon_Current_Price",
            "Amazon_90_Days_Avg_Price",
            "Amazon_90_Days_Drop_Percent",
            "Amazon_90_Days_OOS_Percent",
            "Amazon_Oos_Count_30_Days",
            "Amazon_Oos_Count_90_Days",
            "New_Current_Price",
            "New_90_Days_Avg_Price",
            "New_90_Days_Drop_Percent",
            "New_90_Days_OOS_Percent",
            "New_3rd_Party_FBA_Current_Price",
            "New_3rd_Party_FBA_90_Days_Avg_Price",
            "New_3rd_Party_FBA_90_Days_Drop_Percent",
            "FBA_PickAndPack_Fee",
            "Referral_Fee_Percent",
            "Referral_Fee_Current_Price",
            "New_3rd_Party_FBM_Current_Price",
            "New_3rd_Party_FBM_90_Days_Avg_Price",
            "New_3rd_Party_FBM_90_Days_Drop_Percent",
            "New_Prime_Exclusive_Current_Price",
            "New_Prime_Exclusive_90_Days_Avg_Price",
            "New_Prime_Exclusive_90_Days_Drop_Percent",
            "Lightning_Deals_Current_Price",
            "Used_Current_Price",
            "Used_90_Days_Avg_Price",
            "Used_90_Days_Drop_Percent",
            "Used_90_Days_OOS_Percent",
            "Used_Like_New_Current_Price",
            "Used_Like_New_90_Days_Avg_Price",
            "Used_Like_New_90_Days_Drop_Percent",
            "Used_Very_Good_Current_Price",
            "Used_Very_Good_90_Days_Avg_Price",
            "Used_Very_Good_90_Days_Drop_Percent",
            "Used_Good_Current_Price",
            "Used_Good_90_Days_Avg_Price",
            "Used_Good_90_Days_Drop_Percent",
            "Used_Acceptable_Current_Price",
            "Used_Acceptable_90_Days_Avg_Price",
            "Used_Acceptable_90_Days_Drop_Percent",
            "Warehouse_Deals_Current_Price",
            "Warehouse_Deals_90_Days_Avg_Price",
            "Warehouse_Deals_90_Days_Drop_Percent",
            "List_Price_Current",
            "List_Price_90_Days_Avg",
            "List_Price_90_Days_Drop_Percent",
            "Rental_Current_Price",
            "Rental_90_Days_Avg_Price",
            "Rental_90_Days_Drop_Percent",
            "New_Offer_Count_Current",
            "New_Offer_Count_90_Days_Avg",
            "Count_of_Retrieved_Live_Offers_New_FBA",
            "Count_of_Retrieved_Live_Offers_New_FBM",
            "Used_Offer_Count_Current",
            "Used_Offer_Count_90_Days_Avg",
            "Tracking_Since",
            "Listed_Since",
            "Categories_Root",
            "Categories_Sub",
            "Categories_Tree",
            "Categories_Launchpad",
            "ASIN",
            "Imported_By_Code",
            "Product_Codes_EAN",
            "Product_Codes_UPC",
            "Product_Codes_PartNumber",
            "Parent_ASIN",
            "Variation_ASINs",
            "Freq_Bought_Together",
            "Type",
            "Manufacturer",
            "Brand",
            "Product_Group",
            "Model",
            "Variation_Attributes",
            "Color",
            "Size",
            "Edition",
            "Format",
            "Author",
            "Contributors",
            "Binding",
            "Number_of_Items",
            "Number_of_Pages",
            "Publication_Date",
            "Release_Date",
            "Languages",
            "Package_Dimension_cm3",
            "Package_Weight_g",
            "Package_Quantity",
            "Item_Dimension_cm3",
            "Item_Weight_g",
            "Hazardous_Materials",
            "Is_Hazmat",
            "Is_Heat_Sensitive",
            "Adult_Product",
            "Trade_In_Eligible",
            "Prime_Eligible",
            "Subscribe_and_Save",
            "One_Time_Coupon_Absolute",
            "One_Time_Coupon_Percentage",
            "Subscribe_and_Save_Coupon_Percentage",
            "sys_run_date",
        ]

        headers = [format_header(h) for h in headers]
        # data=data.to_dict(orient='records')
        # Convert column headers
        data.columns = headers

        # List of columns to apply the cleaning functions
        currency_columns = [
            "Buy_Box_Current_Price",
            "Buy_Box_90_Days_Avg_Price",
            "Amazon_Current_Price",
            "Amazon_90_Days_Avg_Price",
            "New_Current_Price",
            "New_90_Days_Avg_Price",
            "New_3rd_Party_FBA_Current_Price",
            "New_3rd_Party_FBA_90_Days_Avg_Price",
            "FBA_PickAndPack_Fee",
            "Referral_Fee_Current_Price",
            "New_3rd_Party_FBM_Current_Price",
            "New_3rd_Party_FBM_90_Days_Avg_Price",
            "New_Prime_Exclusive_Current_Price",
            "New_Prime_Exclusive_90_Days_Avg_Price",
            "Lightning_Deals_Current_Price",
            "Used_Current_Price",
            "Used_90_Days_Avg_Price",
            "Used_Like_New_Current_Price",
            "Used_Like_New_90_Days_Avg_Price",
            "Used_Very_Good_Current_Price",
            "Used_Very_Good_90_Days_Avg_Price",
            "Used_Good_Current_Price",
            "Used_Good_90_Days_Avg_Price",
            "Used_Acceptable_Current_Price",
            "Used_Acceptable_90_Days_Avg_Price",
            "Warehouse_Deals_Current_Price",
            "Warehouse_Deals_90_Days_Avg_Price",
            "List_Price_Current",
            "List_Price_90_Days_Avg",
            "Rental_Current_Price",
            "Rental_90_Days_Avg_Price",
            "One_Time_Coupon_Absolute",
        ]

        percentage_columns = [
            "Sales_Rank_90_Days_Drop_Percent",
            "Buy_Box_90_Days_Drop_Percent",
            "Buy_Box_90_Days_OOS_Percent",
            "Reviews_Review_Count_90_Days_Drop_Percent",
            "Amazon_90_Days_Drop_Percent",
            "Amazon_90_Days_OOS_Percent",
            "New_90_Days_Drop_Percent",
            "New_90_Days_OOS_Percent",
            "New_3rd_Party_FBA_90_Days_Drop_Percent",
            "New_3rd_Party_FBM_90_Days_Drop_Percent",
            "New_Prime_Exclusive_90_Days_Drop_Percent",
            "Used_90_Days_Drop_Percent",
            "Used_Like_New_90_Days_Drop_Percent",
            "Used_Very_Good_90_Days_Drop_Percent",
            "Used_90_Days_OOS_Percent",
            "Used_Good_90_Days_Drop_Percent",
            "Used_Acceptable_90_Days_Drop_Percent",
            "Warehouse_Deals_90_Days_Drop_Percent",
            "List_Price_90_Days_Drop_Percent",
            "Rental_90_Days_Drop_Percent",
            "Referral_Fee_Percent",
            "One_Time_Coupon_Percentage",
            "Subscribe_and_Save_Coupon_Percentage",
            "_90_Days_Change_Percent_Monthly_Sold",
            "Buy_Box_Percent_Amazon_90_Days",
            "Buy_Box_Percent_Top_Seller_90_Days",
        ]

        integer_columns = [
            "Sales_Rank_Current",
            "Sales_Rank_90_Days_Avg",
            "Sales_Rank_Drops_Last_90_Days",
            "Bought_Past_Month",
            "Reviews_Review_Count",
            "Ratings_Format_Specific",
            "Review_Count_Format_Specific",
            "Buy_Box_Stock",
            "New_Offer_Count_Current",
            "New_Offer_Count_90_Days_Avg",
            "Count_of_Retrieved_Live_Offers_New_FBA",
            "Count_of_Retrieved_Live_Offers_New_FBM",
            "Used_Offer_Count_Current",
            "Used_Offer_Count_90_Days_Avg",
            "Number_of_Items",
            "Number_of_Pages",
            "Package_Dimension_cm3",
            "Package_Weight_g",
            "Package_Quantity",
            "Item_Dimension_cm3",
            "Item_Weight_g",
            "Buy_Box_Winner_Count_90_Days",
            "Amazon_Oos_Count_30_Days",
            "Amazon_Oos_Count_90_Days",
        ]

        # Apply cleaning functions to the specified columns
        for col in currency_columns:
            data[format_header(col)] = data[format_header(col)].apply(clean_currency)

        for col in percentage_columns:
            data[format_header(col)] = data[format_header(col)].apply(clean_percentage)

        for col in integer_columns:
            data[format_header(col)] = (
                data[format_header(col)].astype(float).fillna(0).astype(int)
            )

        # Apply the clean_data function to all elements in the dataframe
        data = data.map(clean_data)
        # Replace NaNs with None
        data = data.where(pd.notnull(data), None)

        # Add primary key column
        data["pk_column_name"] = data.apply(
            lambda row: (
                (str(row["asin"]) + str(row["sys_run_date"]))
                if row["asin"] and row["sys_run_date"]
                else None
            ),
            axis=1,
        )
        data_dict = data.to_dict(orient="records")
        # Apply clean_data to each value in data_dict
        cleaned_data_dict = [
            {k: clean_data(v) for k, v in record.items()} for record in data_dict
        ]

        # Specify the batch size
        batch_size = 1000  # Adjust the batch size as needed

        # Function to insert data in batches
        def batch_insert(data, batch_size):
            total_batches = math.ceil(len(data) / batch_size)
            for i in range(total_batches):
                batch = data[i * batch_size : (i + 1) * batch_size]
                try:
                    response = (
                        supabase.table("keepa_product_viewer_data")
                        .upsert(batch)
                        .execute()
                    )
                    if hasattr(response, "error") and response.error is not None:
                        raise Exception(f"Error inserting rows: {response.error}")
                    print(f"Batch {i + 1}/{total_batches} inserted successfully")
                except Exception as e:
                    print(f"Error upserting batch {i + 1}/{total_batches}: {e}")
                    # Add a small delay to avoid overwhelming the server
                    time.sleep(2)

        # Perform batch insertions
        batch_insert(cleaned_data_dict, batch_size)
    except Exception as e:
        print(e)


# keepa_viewer(
#     r"C:\Users\tran\OneDrive\Documents\Amazon Scraping\Keepa_Sourcing_Listing_Tool\all_asins.txt"
# )
