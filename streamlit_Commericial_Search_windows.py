import os
import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import streamlit as st
from pathlib import Path  # Ensure cross-platform paths

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

# Define User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

# Function to clean filenames (Handles Windows-specific constraints)
def clean_filename(url, unique_suffix):
    """Create a valid filename from a URL and add a unique suffix."""
    slug = re.sub(r'[<>:"/\\|?*]', '_', url.split('/')[-1])  # Replace invalid characters
    return f"{slug}_{unique_suffix}.html"  # Unique filename with suffix

# Function to scrape links
def scrape_links(url, css_selector):
    """Scrape links from a given URL."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        st.error(f"Failed to fetch page: {url}, status code: {response.status_code}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    return [a['href'] for a in soup.select(css_selector)]

# Function to save HTML content locally
def save_html_content(link, directory, unique_suffix, original_urls):
    """Download article HTML and save it locally."""
    response = requests.get(link, headers=HEADERS)
    if response.status_code != 200:
        st.error(f"Failed to fetch article: {link}, status code: {response.status_code}")
        return
    
    # Ensure the directory exists (cross-platform)
    directory = Path(directory)  # Convert to Path object
    directory.mkdir(parents=True, exist_ok=True)
    
    file_name = clean_filename(link, unique_suffix)
    file_path = directory / file_name  # Cross-platform file path
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    
    original_urls[file_name] = link  # Store mapping
    st.info(f"Saved: {file_path}")

# Streamlit UI
st.title("Web Scraping and Parsing Application")
st.write("This application scrapes articles from Commercial Search's website for various asset types (Office, Industrial, Retail, etc.). Users can specify the number of pages to scrape and where to save the HTML files. The scraper extracts article links, downloads their content, and stores them locally for further analysis.")

selected_category = st.selectbox("Choose a category to scrape:", list(BASE_URLS.keys()))
base_url = BASE_URLS[selected_category]

num_pages = st.number_input("Enter the number of pages to scrape:", min_value=1, value=1)
save_directory = st.text_input("Enter the directory to save HTML files:")

if st.button("Start Scraping"):
    if base_url and save_directory:
        with st.spinner("Scraping in progress..."):
            try:
                save_directory = Path(save_directory)  # Convert to cross-platform Path
                save_directory.mkdir(parents=True, exist_ok=True)
                
                original_urls = {}
                urls = [f"{base_url}page/{i}/" for i in range(1, num_pages + 1)]
                
                article_count = 0
                for page_url in urls:
                    links = scrape_links(page_url, ".cpe-posts-category-page .fl-post-title a")
                    for link in links:
                        article_count += 1
                        save_html_content(link, save_directory, article_count, original_urls)
                        time.sleep(2)  # Pause to prevent getting blocked
                
                st.success("Scraping completed!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please fill in all required fields.")
