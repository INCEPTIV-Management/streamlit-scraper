import os
import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import streamlit as st

# Define asset type keywords
ASSET_TYPE_KEYWORDS = ["Office", "Industrial", "Retail", "Medical Office", "Coworking", "Data Centers"]

# Predefined list of base URLs
BASE_URLS = {
    "Office": "https://www.commercialsearch.com/news/office/",
    "Industrial": "https://www.commercialsearch.com/news/industrial/",
    "Retail": "https://www.commercialsearch.com/news/retail/",
    "Medical Office": "https://www.commercialsearch.com/news/medical-office/",
    "Coworking": "https://www.commercialsearch.com/news/coworking/",
    "Data Centers": "https://www.commercialsearch.com/news/data-centers/"
}

# Hardcoded CSS selectors (from your original code)
CSS_SELECTORS = {
    "article_links": ".cpe-posts-category-page .fl-post-title a",  # Selector for article links
    "title": ".fl-node-r05xkta16lp9 .fl-heading-text",  # Selector for article title
    "date": ".fl-post-info-date",  # Selector for article date
    "tags": ".post_categories",  # Selector for tags
    "companies": ".fl-post-info-terms a"  # Selector for related companies
}

# Function to scrape links
def scrape_links(url, css_selector):
    """Scrape links based on the provided URL and CSS selector."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch page: {url}, status code: {response.status_code}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    links = [a['href'] for a in soup.select(css_selector)]
    st.info(f"Found {len(links)} links on {url}.")  # Debug: Number of links found
    return links

# Function to generate URLs
def generate_urls(base_url, num_pages):
    """Generate URLs for the most recent `num_pages` pages."""
    return [f"{base_url}page/{i}/" for i in range(1, num_pages + 1)]

# Function to clean filenames
def clean_filename(url, unique_suffix):
    """Create a valid filename from a URL and add a unique suffix."""
    slug = re.sub(r'[^\w\-]', '_', url.split('/')[-1])  # Clean the slug
    return f"{slug}_{unique_suffix}.html"  # Unique filename with suffix

# Function to save HTML content
def save_html_content(link, directory, unique_suffix):
    """Save HTML content of a given link to a file."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    response = requests.get(link, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch article: {link}, status code: {response.status_code}")
        return
    file_name = clean_filename(link, unique_suffix)  # Create a unique filename
    file_path = os.path.join(directory, file_name)

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        st.info(f"Saved: {file_path}")  # Debug: Confirm file saved
    except Exception as e:
        st.error(f"Error saving file {file_name}: {e}")

# Function to extract asset type
def extract_asset_type(tags):
    """Extract the asset type from the tags based on predefined keywords."""
    for tag in tags:
        for keyword in ASSET_TYPE_KEYWORDS:
            if keyword.lower() in tag.lower():  # Case-insensitive match
                return keyword
    return None  # Return None if no match is found

# Function to parse HTML files
def parse_html_file(file_path, title_css, date_css, tags_css, companies_css):
    """Parse an HTML file and extract article details along with transaction information."""
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
   
    # Extracting the data using provided CSS selectors
    title = soup.select_one(title_css).get_text(strip=True) if soup.select_one(title_css) else None
    date = soup.select_one(date_css).get_text(strip=True) if soup.select_one(date_css) else None
    tags_div = soup.select_one(tags_css)
    tags = [a.get_text(strip=True) for a in tags_div.select('a') if a.get_text(strip=True) != "More"] if tags_div else []
    companies = [company.get_text(strip=True) for company in soup.select(companies_css)] if soup.select(companies_css) else []
 
    # Extract the first two meaningful paragraphs
    first_paragraph, second_paragraph = extract_first_two_content_paragraphs(soup)
   
    # Combine the first and second paragraphs for transaction extraction
    combined_paragraphs = (first_paragraph or '') + ' ' + (second_paragraph or '')
 
    # Extract transaction information using regex from the combined paragraphs
    transaction_info = extract_transaction_info(combined_paragraphs)

    # Extract region from tags
    region = extract_region(tags)

    # Extract asset type from tags
    asset_type = extract_asset_type(tags)
 
    return {
        "Article Title": title,
        "Article URL": file_path,  # Use the file path as the URL
        "Date Published": date,
        "Tags": ', '.join(tags),
        "Region": region,  # Add region to the return dictionary
        "Asset Type": asset_type,  # Add asset type to the return dictionary
        "Intro Paragraph": second_paragraph,  # Use the first paragraph as the intro
        "Company": None,  # Placeholder for Company (you can update this logic if needed)
        "Related Companies": ', '.join(companies),
        "Transaction Amount": transaction_info.get("Transaction Amount"),
        "Square Footage": transaction_info.get("Square Footage"),
        "Asset Descriptor": ', '.join(transaction_info.get("Asset Descriptor", [])),
    }

# Function to extract region
def extract_region(tags):
    """Extract region from tags."""
    regions = ["Northeast", "West", "Southwest", "Southeast", "Midwest", "Mid-Atlantic"]
    for tag in tags:
        if tag in regions:
            return tag
    return "Unknown"  # Return "Unknown" if no region is found in tags

# Function to extract first two content paragraphs
def extract_first_two_content_paragraphs(soup):
    """Extract the first two content paragraphs, ignoring metadata and non-content tags."""
    paragraphs = soup.find_all('p')
 
    # Filter out paragraphs that are too short or likely to be metadata
    content_paragraphs = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if is_content_paragraph(text):
            content_paragraphs.append(text)
            if len(content_paragraphs) == 2:
                break  # Stop after collecting two content paragraphs
 
    # Extract the first and second content paragraphs
    first_paragraph = content_paragraphs[0] if len(content_paragraphs) > 0 else None
    second_paragraph = content_paragraphs[1] if len(content_paragraphs) > 1 else None
 
    return first_paragraph, second_paragraph
 
# Function to check if a paragraph is content
def is_content_paragraph(text):
    """Determine if a paragraph is likely to be content rather than metadata."""
    # Skip paragraphs that are too short or contain typical metadata keywords
    if len(text) < 20:
        return False
    # Add more rules here if needed, like checking for specific patterns of metadata
    metadata_keywords = ['by', 'posted on', 'updated', 'author', 'date', 'category', 'tags']
    return not any(keyword.lower() in text.lower() for keyword in metadata_keywords)
 
# Function to extract transaction information
def extract_transaction_info(paragraphs):
    """Extract transaction information using regex from combined paragraphs."""
    extracted_info = {
        "Transaction Amount": None,
        "Square Footage": None,
        "Asset Descriptor": [],
        "Companies Involved": []
    }
 
    if not paragraphs:
        return extracted_info  # Return empty info if no paragraphs
 
    # Regex patterns for extraction
    amount_pattern = r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?) million'
    size_pattern = r'(\d{1,3}(?:,\d{3})*)-square-foot'
   
    # Find transaction amount
    amount_match = re.search(amount_pattern, paragraphs)
    if amount_match:
        extracted_info["Transaction Amount"] = amount_match.group(0)
 
    # Find square footage
    size_match = re.search(size_pattern, paragraphs)
    if size_match:
        extracted_info["Square Footage"] = size_match.group(1).replace(',', '')
 
    # Find geographic locations and companies mentioned
    locations = re.findall(r'\b(?:in|near)\s+([A-Za-z\s,]+)', paragraphs)
    if locations:
        extracted_info["Asset Descriptor"] = list(set(loc.strip() for loc in locations))
 
    return extracted_info
 
# Function to parse all HTML files in a directory
def parse_html_files(directory, title_css, date_css, tags_css, companies_css):
    """Main function to parse all HTML files in the specified directory."""
    all_data = []
   
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            article_data = parse_html_file(file_path, title_css, date_css, tags_css, companies_css)
            article_data["File Name"] = filename  # Add the filename to the data
            all_data.append(article_data)
   
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_data)
   
    # Reorder the columns as per the specified order
    column_order = [
        "Article Title", "Article URL", "Date Published", "Tags", "Region", "Asset Type",
        "Intro Paragraph", "Company", "Related Companies", "Transaction Amount",
        "Square Footage", "Asset Descriptor"
    ]
    df = df[column_order]
   
    return df

# Streamlit UI
st.title("Web Scraping and Parsing Application")

# Dropdown for base URL selection
selected_category = st.selectbox("Choose a category to scrape:", list(BASE_URLS.keys()))
base_url = BASE_URLS[selected_category]

# User inputs
num_pages = st.number_input("Enter the number of pages to scrape:", min_value=1, value=1)
save_directory = st.text_input("Enter the directory to save HTML files (e.g., /Users/StephanieLei/Documents/INCEPTIV/html_files_retail6):")

# Button to start scraping
if st.button("Start Scraping and Parsing"):
    if base_url and save_directory:
        with st.spinner("Scraping and parsing in progress..."):
            try:
                # Create directory if it doesn't exist
                os.makedirs(save_directory, exist_ok=True)

                # Generate URLs for the specified number of pages
                urls = generate_urls(base_url, num_pages)
                
                # Scrape links and save HTML content
                article_count = 0
                for page_url in urls:
                    st.info(f"Scraping page: {page_url}")
                    links = scrape_links(page_url, CSS_SELECTORS["article_links"])
                    for link in links:
                        st.info(f"Processing link: {link}")
                        article_count += 1
                        save_html_content(link, save_directory, article_count)  # Save HTML content
                        time.sleep(2)  # Pause to avoid overwhelming the server

                # Parse HTML files and generate DataFrame
                df = parse_html_files(save_directory, CSS_SELECTORS["title"], CSS_SELECTORS["date"], CSS_SELECTORS["tags"], CSS_SELECTORS["companies"])

                # Save DataFrame to Excel
                excel_file = os.path.join(save_directory, "parsed_articles.xlsx")
                df.to_excel(excel_file, index=False)

                st.success("Scraping and parsing completed successfully!")

                # Provide download link for the Excel file
                with open(excel_file, "rb") as file:
                    st.download_button(
                        label="Download Excel File",
                        data=file,
                        file_name="parsed_articles.xlsx",
                        mime="application/vnd.ms-excel"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill in all the required fields.")

#process to run:
# cd "Streamlit App"
# streamlit run testing2.py