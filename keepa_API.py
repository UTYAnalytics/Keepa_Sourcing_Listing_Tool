import requests
import json
import time

def fetch_keepa_asins(api_key, domain, selection, output_file):
    """
    Fetches ASINs from Keepa API based on the provided selection criteria and writes them to a file.
    
    Parameters:
    - api_key: str, your Keepa API key
    - domain: int, the domain id for the request
    - selection: dict, the selection criteria for the request
    - output_file: str, the file path to save the ASINs
    
    Returns:
    - None
    """
    def fetch_data(page):
        selection["page"] = page
        api_url = f"https://api.keepa.com/query?key={api_key}&domain={domain}&selection={json.dumps(selection)}"
        response = requests.get(api_url)
        return response

    all_asins = []
    current_page = 0
    total_results = 0

    while True:
        # Fetch data for the current page
        response = fetch_data(current_page)
        
        # Check the status code
        if response.status_code == 200:
            page_data = response.json()
        elif response.status_code == 429:
            # Handle rate limit
            retry_after = response.json().get("refillIn", 60000) / 1000  # Default to 60 seconds if not provided
            print(f"Rate limit exceeded. Waiting for {retry_after} seconds...")
            time.sleep(retry_after)
            continue  # Retry the current page after waiting
        else:
            print(f"Error: Failed to fetch data for page {current_page}. Status code: {response.status_code}")
            print(response.text)
            break

        # Append the current page data to all_asins
        if "asinList" in page_data:
            all_asins.extend(page_data["asinList"])
        else:
            break
        
        # Increment the current page
        current_page += 1
        
        # Update the total_results
        total_results = page_data.get("totalResults", 0)
        
        # If we have fetched all the results, break the loop
        if len(all_asins) >= total_results:
            break

        # Check for token limit and wait if needed
        tokens_left = page_data.get("tokensLeft", 0)
        if tokens_left <= 0:
            refill_in = page_data.get("refillIn", 0) / 1000  # Convert milliseconds to seconds
            print(f"Waiting for {refill_in} seconds to refill tokens...")
            time.sleep(refill_in)

    # Write the ASINs to the output file
    with open(output_file, "w") as file:
        file.write(",".join(all_asins))

    print(f"Data exported to {output_file}")

