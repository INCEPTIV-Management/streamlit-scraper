import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_commercial_search_industrial(pages):
    """
    Scrapes articles from the Commercial Search website for the industrial property type.
    """
    base_url = "https://www.commercialsearch.com/news/industrial/"
    data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for page in range(1, pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"

        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Debug: Print a portion of the HTML to verify structure
            print(f"HTML Content (Partial): {soup.prettify()[:1000]}")
            
            # Update this based on the actual structure of the articles
            articles = soup.find_all('div', {'class': 'post-item'})  # Example class for articles
            print(f"Number of articles found: {len(articles)}")

            for article in articles:
                title = article.find('h2').text.strip() if article.find('h2') else None
                link = article.find('a')['href'] if article.find('a') else None
                date = article.find('time')['datetime'] if article.find('time') else None
                intro = article.find('p').text.strip() if article.find('p') else None
                data.append([title, date, link, intro])
        else:
            print(f"Failed to fetch URL: {url}. Status Code: {response.status_code}")

    return data


def save_to_csv(data, file_name):
    """
    Saves the scraped data to a CSV file.
    """
    df = pd.DataFrame(data, columns=["Article Title", "Date", "Link", "Intro Paragraph"])
    df.to_csv(file_name, index=False, encoding="utf-8")
    print(f"Data saved to {file_name}")

# Number of pages to scrape
pages_to_scrape = 3  # Adjust as needed

# Scrape data
scraped_data = scrape_commercial_search_industrial(pages_to_scrape)

# Save data to CSV
if scraped_data:
    save_to_csv(scraped_data, "commercial_search_industrial.csv")
else:
    print("No data was scraped.")
