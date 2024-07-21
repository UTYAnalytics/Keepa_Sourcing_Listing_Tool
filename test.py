import unicodedata

def format_header(header):
    # Convert to title case
    header = header.title()
    # Replace spaces with underscores
    header = header.replace(" ", "_")
    # Replace special characters with underscore
    header = header.replace("🚚", "")
    header = header.replace(":", "")
    header = header.replace("-", "")
    # Remove Vietnamese characters by decomposing and keeping only ASCII
    header = (
        unicodedata.normalize("NFKD", header)
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )
    return header

headers = [
    "Locale", "Image", "Title", "Sales Rank: Current", "Sales Rank: 90 days avg.", 
    "Sales Rank: 90 days drop %", "Sales Rank: Drops last 90 days", "Sales Rank: Reference", 
    "Sales Rank: Subcategory Sales Ranks", "Bought in past month", "90 days change % monthly sold", 
    "Reviews: Rating", "Reviews: Review Count", "Reviews: Review Count - 90 days drop %", 
    "Reviews: Ratings - Format Specific", "Reviews: Review Count - Format Specific", 
    "Last Price Change", "Buy Box 🚚: Current", "Buy Box 🚚: 90 days avg.", "Buy Box 🚚: 90 days drop %", 
    "Buy Box 🚚: Stock", "Buy Box 🚚: 90 days OOS", "Buy Box Seller", "Buy Box: % Amazon 90 days", 
    "Buy Box: % Top Seller 90 days", "Buy Box: Winner Count 90 days", "Buy Box: Is FBA", "Buy Box: Unqualified", 
    "Amazon: Current", "Amazon: 90 days avg.", "Amazon: 90 days drop %", "Amazon: 90 days OOS", 
    "Amazon: OOS Count 30 days", "Amazon: OOS Count 90 days", "New: Current", "New: 90 days avg.", 
    "New: 90 days drop %", "New: 90 days OOS", "New, 3rd Party FBA: Current", "New, 3rd Party FBA: 90 days avg.", 
    "New, 3rd Party FBA: 90 days drop %", "FBA Pick&Pack Fee", "Referral Fee %", "Referral Fee based on current Buy Box price", 
    "New, 3rd Party FBM 🚚: Current", "New, 3rd Party FBM 🚚: 90 days avg.", "New, 3rd Party FBM 🚚: 90 days drop %", 
    "New, Prime exclusive: Current", "New, Prime exclusive: 90 days avg.", "New, Prime exclusive: 90 days drop %", 
    "Lightning Deals: Current", "Used: Current", "Used: 90 days avg.", "Used: 90 days drop %", "Used: 90 days OOS", 
    "Used, like new 🚚: Current", "Used, like new 🚚: 90 days avg.", "Used, like new 🚚: 90 days drop %", 
    "Used, very good 🚚: Current", "Used, very good 🚚: 90 days avg.", "Used, very good 🚚: 90 days drop %", 
    "Used, good 🚚: Current", "Used, good 🚚: 90 days avg.", "Used, good 🚚: 90 days drop %", 
    "Used, acceptable 🚚: Current", "Used, acceptable 🚚: 90 days avg.", "Used, acceptable 🚚: 90 days drop %", 
    "Warehouse Deals: Current", "Warehouse Deals: 90 days avg.", "Warehouse Deals: 90 days drop %", 
    "List Price: Current", "List Price: 90 days avg.", "List Price: 90 days drop %", "Rental: Current", 
    "Rental: 90 days avg.", "Rental: 90 days drop %", "New Offer Count: Current", "New Offer Count: 90 days avg.", 
    "Count of retrieved live offers: New, FBA", "Count of retrieved live offers: New, FBM", 
    "Used Offer Count: Current", "Used Offer Count: 90 days avg.", "Tracking since", "Listed since", 
    "Categories: Root", "Categories: Sub", "Categories: Tree", "Categories: Launchpad", "ASIN", "Imported by Code", 
    "Product Codes: EAN", "Product Codes: UPC", "Product Codes: PartNumber", "Parent ASIN", "Variation ASINs", 
    "Freq. Bought Together", "Type", "Manufacturer", "Brand", "Product Group", "Model", "Variation Attributes", 
    "Color", "Size", "Edition", "Format", "Author", "Contributors", "Binding", "Number of Items", "Number of Pages", 
    "Publication Date", "Release Date", "Languages", "Package: Dimension (cm³)", "Package: Weight (g)", 
    "Package: Quantity", "Item: Dimension (cm³)", "Item: Weight (g)", "Hazardous Materials", "Is HazMat", 
    "Is heat sensitive", "Adult Product", "Trade-In Eligible", "Prime Eligible (Buy Box)", "Subscribe and Save", 
    "One Time Coupon: Absolute", "One Time Coupon: Percentage", "Subscribe and Save Coupon: Percentage", 
    "sys_run_date", "pk_column_name"
]

formatted_headers = [format_header(header) for header in headers]
print(formatted_headers)
