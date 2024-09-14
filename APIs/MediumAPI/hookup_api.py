import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the URL of your Medium homepage
MEDIUM_HOME_URL = "https://medium.com/me/dashboard"

# Load the session cookie from the .env file
COOKIE_VALUE = os.getenv("COOKIE")
if not COOKIE_VALUE:
    raise ValueError("No COOKIE value found. Please set it in your .env file.")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Cookie": COOKIE_VALUE
}

def fetch_daily_article_link():
    # Send a GET request to Medium's dashboard
    response = requests.get(MEDIUM_HOME_URL, headers=HEADERS)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve content: HTTP {response.status_code}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the daily article link by using string parameter
    daily_article = soup.find('a', href=True, string="Your Daily Read")
    print(soup)
#     if daily_article:
#         link = daily_article['href']
#         if not link.startswith("https"):
#             link = "https://medium.com" + link
#         return link
#     else:
#         print("Daily article link not found.")
#         return None

def main():
    daily_article_link = fetch_daily_article_link()
    
    if daily_article_link:
        print(f"Your daily article link: {daily_article_link}")
    else:
        print("Could not retrieve the daily article link.")

if __name__ == "__main__":
    main()
