import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
import os

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, num_results=3):
        self.num_results = num_results
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_search_results(self, query):
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        try:
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('div', class_='yuRUbf')
            urls = [result.find('a')['href'] for result in search_results[:self.num_results]]
            return urls
        except Exception as e:
            logger.error(f"Error getting search results for query '{query}': {str(e)}")
            return []

    def scrape_website(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            
            text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""
            
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = re.sub(r'\n+', '\n', text_content) 
            
            title = soup.title.string if soup.title else ""
            
            with open('debug/results.txt', "a") as f:
                f.write(f"URL: {url}\n")
                f.write(f"Title: {title}\n")
                f.write(f"Content: {text_content[:500]}...\n")
                f.write("---\n\n")
            
            return {
                "url": url,
                "title": title,
                "content": text_content[:5000],  # Limit content to first 5000 characters
                "error": None
            }
        except Exception as e:
            logger.error(f"Error scraping website {url}: {str(e)}")
            return {"url": url, "title": "", "content": "", "error": str(e)}

    def search_and_scrape(self, topic):
        logger.info(f"Starting search and scrape for topic: {topic}")
        
        urls = self.get_search_results(topic)
        
        if not urls:
            logger.warning(f"No search results found for topic: {topic}")
            return []

        results = []
        
        for url in urls:
            data = self.scrape_website(url)
            results.append(data)
            logger.info(f"Scraped data from {url}")
        
        return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Scraper()
    test_topic = "Brazilian Central Bank latest data"
    results = scraper.search_and_scrape(test_topic)
    print(f"Found {len(results)} results for topic: {test_topic}")
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Content snippet: {result['content'][:200]}...")  # First 200 characters
        print("---")