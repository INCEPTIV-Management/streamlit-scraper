'''
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import csv

def scrape_multihousing_news(pages, property_type):
    """
    Function to scrape Multi-Housing News articles for a specific property type.
    """
    base_url = f"https://www.multihousingnews.com/tag/{property_type}/page/"
    data = []
    for page in range(1, pages + 1):
        url = f"{base_url}{page}/"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all('article')
            for article in articles:
                title = article.find('h2', {'class': 'entry-title'}).text.strip() if article.find('h2') else ""
                link = article.find('a')['href'] if article.find('a') else ""
                date = article.find('time')['datetime'] if article.find('time') else ""
                intro = article.find('div', {'class': 'entry-excerpt'}).text.strip() if article.find('div', {'class': 'entry-excerpt'}) else ""
                data.append([title, date, link, "", "", intro, "", "", ""])
        else:
            st.warning(f"Failed to access Multi-Housing News page {page}.")
    return data

def scrape_commercial_search(pages, property_type):
    """
    Function to scrape Commercial Search articles for a specific property type.
    """
    base_url = f"https://www.commercialsearch.com/news/tag/{property_type}/page/"
    data = []
    for page in range(1, pages + 1):
        url = f"{base_url}{page}/"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all('article')
            for article in articles:
                title = article.find('h2').text.strip() if article.find('h2') else ""
                link = article.find('a')['href'] if article.find('a') else ""
                date = article.find('time')['datetime'] if article.find('time') else ""
                intro = article.find('p').text.strip() if article.find('p') else ""
                data.append([title, date, link, "", "", intro, "", "", ""])
        else:
            st.warning(f"Failed to access Commercial Search page {page}.")
    return data

def scrape_traded(pages):
    """
    Function to scrape Traded articles.
    """
    base_url = "https://traded.co/page/"
    data = []
    for page in range(1, pages + 1):
        url = f"{base_url}{page}/"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all('div', {'class': 'content-card'})
            for article in articles:
                title = article.find('h2').text.strip() if article.find('h2') else ""
                link = article.find('a')['href'] if article.find('a') else ""
                date = article.find('span', {'class': 'date'}).text.strip() if article.find('span', {'class': 'date'}) else ""
                intro = article.find('p').text.strip() if article.find('p') else ""
                data.append([title, date, link, "", "", intro, "", "", ""])
        else:
            st.warning(f"Failed to access Traded page {page}.")
    return data

def create_csv(data):
    """
    Create CSV file from the scraped data.
    """
    output = BytesIO()
    df = pd.DataFrame(data, columns=[
        "Article Title", "Date", "Link to Article", "Asset Descriptor", "Asset Type", "Intro Paragraph", "Region", "Location", "$ Value"
    ])
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

# Streamlit app
st.title("Web Scraper for Real Estate Websites")

website_choice = st.selectbox(
    "Select a website to scrape:",
    ("Multi-Housing News", "Commercial Search", "Traded")
)

property_type = None
if website_choice == "Multi-Housing News":
    property_type = st.selectbox(
        "Select a property type:",
        ["market-rate", "luxury", "affordable-housing", "student-housing", "senior-housing", 
         "manufactured-housing", "condo", "military-housing", "self-storage", "single-family-rental"]
    )
elif website_choice == "Commercial Search":
    property_type = st.selectbox(
        "Select a property type:",
        ["office", "industrial", "retail", "medical-office", "coworking", "data-centers"]
    )

pages = st.number_input("Number of pages to scrape:", min_value=1, max_value=100, value=1, step=1)

if st.button("Scrape Data"):
    st.info("Scraping data... Please wait.")
    if website_choice == "Multi-Housing News" and property_type:
        data = scrape_multihousing_news(pages, property_type)
    elif website_choice == "Commercial Search" and property_type:
        data = scrape_commercial_search(pages, property_type)
    elif website_choice == "Traded":
        data = scrape_traded(pages)
    else:
        st.error("Please select a property type for the selected website.")
        data = []

    if data:
        st.success(f"Scraped {len(data)} articles.")
        csv_file = create_csv(data)
        st.download_button(
            label="Download CSV",
            data=csv_file,
            file_name="scraped_data.csv",
            mime="text/csv"
        )
    else:
        st.error("No data was scraped. Try again later.")
        '''
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import csv

def parse_html(file_content, title_css, date_css, tags_css, paragraph_css, companies_css):
    """
    Parse HTML content and extract article details.
    """
    soup = BeautifulSoup(file_content, "html.parser")

    # Extracting the data using provided CSS selectors
    title = soup.select_one(title_css).get_text(strip=True) if soup.select_one(title_css) else None
    date = soup.select_one(date_css).get_text(strip=True) if soup.select_one(date_css) else None

    # Extract tags
    tags_div = soup.select_one(tags_css)
    tags = [a.get_text(strip=True) for a in tags_div.select('a') if a.get_text(strip=True) != "More"] if tags_div else []

    # Locate the first paragraph
    paragraph = soup.select_one(paragraph_css).get_text(strip=True) if soup.select_one(paragraph_css) else None

    # Extract related companies
    companies = [company.get_text(strip=True) for company in soup.select(companies_css)] if soup.select(companies_css) else []

    return {
        "Title": title,
        "Date": date,
        "Tags": ', '.join(tags),
        "Introductory Paragraph": paragraph,
        "Related Companies": ', '.join(companies)
    }

def scrape_commercial_search(pages, property_type):
    base_url = f"https://www.commercialsearch.com/news/{property_type}/"
    data = []
    for page in range(1, pages + 1):
        url = base_url if page == 1 else f"{base_url}page/{page}/"
        print(f"Fetching URL: {url}")  # Log URL
        response = requests.get(url)
        print(f"Response Status Code: {response.status_code}")  # Log status code
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            print(f"HTML Content (Partial): {soup.prettify()[:1000]}")  # Log partial HTML
            articles = soup.find_all('article')
            print(f"Number of articles found: {len(articles)}")  # Log article count
            for article in articles:
                title = article.find('h2').text.strip() if article.find('h2') else ""
                link = article.find('a')['href'] if article.find('a') else ""
                date = article.find('time')['datetime'] if article.find('time') else ""
                intro = article.find('p').text.strip() if article.find('p') else ""
                data.append([title, date, link, "", "", intro, "", "", ""])
        else:
            print(f"Failed to fetch URL: {url}")
            st.warning(f"Failed to access {url}. Status Code: {response.status_code}")
    return data


def scrape_traded(pages):
    """
    Function to scrape Traded articles.
    """
    base_url = "https://traded.co/page/"
    data = []
    for page in range(1, pages + 1):
        url = f"{base_url}{page}/"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all('div', {'class': 'content-card'})
            for article in articles:
                title = article.find('h2').text.strip() if article.find('h2') else ""
                link = article.find('a')['href'] if article.find('a') else ""
                date = article.find('span', {'class': 'date'}).text.strip() if article.find('span', {'class': 'date'}) else ""
                intro = article.find('p').text.strip() if article.find('p') else ""
                data.append([title, date, link, "", "", intro, "", "", ""])
        else:
            st.warning(f"Failed to access Traded page {page}.")
    return data

def create_csv(data):
    """
    Create CSV file from the scraped data.
    """
    output = BytesIO()
    df = pd.DataFrame(data, columns=[
        "Article Title", "Date", "Link to Article", "Asset Descriptor", "Asset Type", "Intro Paragraph", "Region", "Location", "$ Value"
    ])
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

# Streamlit app
st.title("Web Scraper for Real Estate Websites")

website_choice = st.selectbox(
    "Select a website to scrape:",
    ("Multi-Housing News", "Commercial Search", "Traded")
)

property_type = None
if website_choice == "Multi-Housing News":
    property_type = st.selectbox(
        "Select a property type:",
        ["market-rate", "luxury", "affordable-housing", "student-housing", "senior-housing", 
         "manufactured-housing", "condo", "military-housing", "self-storage", "single-family-rental"]
    )
elif website_choice == "Commercial Search":
    property_type = st.selectbox(
        "Select a property type:",
        ["office", "industrial", "retail", "medical-office", "coworking", "data-centers"]
    )

pages = st.number_input("Number of pages to scrape:", min_value=1, max_value=100, value=1, step=1)

if st.button("Scrape Data"):
    st.info("Scraping data... Please wait.")
    if website_choice == "Multi-Housing News" and property_type:
        data = scrape_multihousing_news(pages, property_type)
    elif website_choice == "Commercial Search" and property_type:
        data = scrape_commercial_search(pages, property_type)
    elif website_choice == "Traded":
        data = scrape_traded(pages)
    else:
        st.error("Please select a property type for the selected website.")
        data = []

    if data:
        st.success(f"Scraped {len(data)} articles.")
        csv_file = create_csv(data)
        st.download_button(
            label="Download CSV",
            data=csv_file,
            file_name="scraped_data.csv",
            mime="text/csv"
        )
    else:
        st.error("No data was scraped. Try again later.")


