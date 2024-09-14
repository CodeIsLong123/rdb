import requests
import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
from transformers import pipeline

# Load environment variables
load_dotenv()

# News API Client Class (entferne doppelte Definition)
class NewsApiClient: 
    def __init__(self): 
        self.api_key = os.getenv('NEWS_API_KEY')
        self.url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.api_key}"

    def get_top_5_articles(self, country='us', category='general', page_size=5):
        try:
            url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&pageSize={page_size}&apiKey={self.api_key}"
            response = requests.get(url)
            articles = response.json()['articles']  
            status = response.json()['status']  
            if status == "ok":
                return articles 
            else:
                return []   
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []   
        
    def cleanup_articles(self, articles):
        cleaned_articles = []
        for article in articles:
            title = article['title']
            description = article['description']
            url = article['url']
            cleaned_articles.append({'title': title, 'description': description, 'url': url})
        return cleaned_articles

# TagesSchaueClient für die Tagesschau API
class TagesSchaueClient:
    def __init__(self): 
        self.api_key = os.getenv('TAGES_SCHAU_API_KEY')
        self.tagesschau_api = "https://tagesschau.de/api2u/homepage"
        self.summerizer = pipeline("summarization", model="Falconsai/text_summarization")
    def get_articles(self):
        try:
            response = requests.get(self.tagesschau_api)
            articles = response.json().get('news', [])  # Safely get 'news' key
            return articles
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []
    
    def clean_html(self, text):
        # Entfernen von HTML-Markup und leeren Zeichen
        return BeautifulSoup(text, "html.parser").get_text()

    def summarize_articles(self, article):
        # Summarize article using pipeline
        summary = self.summerizer(article)
        print("--------------------------------------------")
        print(summary)
        print("--------------------------------------------")
        return summary

    def cleanup_articles(self, articles):
        cleaned_articles = []
        for article in articles:
            title = article.get('title', 'No title')
            date = article.get('date', 'No date')
            link = article.get('detailsweb', 'No link')
            
            # Extract text content from 'content' if it's present
            content = article.get('content', [])
            text_content = [item['value'] for item in content if item['type'] == 'text']
            text_content = " ".join(text_content)  # Join all text pieces

            text_content = self.clean_html(text_content)    

            ## summarize article
            summary = self.summarize_articles(text_content)
            cleaned_articles.append({
                'title': title,
                'date': date,
                'link': link,
                'text_content': summary[0]['summary_text']
            })


        return cleaned_articles


# Article summarizer class

if __name__ == "__main__":
    tages_schau = TagesSchaueClient()

    articles = tages_schau.get_articles()
    cleaned_articles = tages_schau.cleanup_articles(articles)
    print(cleaned_articles)

