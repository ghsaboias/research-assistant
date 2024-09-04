import logging
import requests
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import concurrent.futures
from requests.exceptions import RequestException
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
from config import CONFIG

# Set up logging
logger = logging.getLogger(__name__)

def fetch_data_with_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service()
    
    try:
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            driver.get(url)
            WebDriverWait(driver, CONFIG["SELENIUM_TIMEOUT"]).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return driver.page_source
    except Exception as e:
        logger.error(f"Error fetching data from {url}: {str(e)}")
    
    return None

def scrape_website(url):
    try:
        html_content = fetch_data_with_selenium(url)
        if not html_content:
            return {"content": [], "headlines": [], "lists": [], "error": "Failed to fetch content"}

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all paragraph texts
        paragraphs = soup.find_all('p')
        content = [p.text.strip() for p in paragraphs if len(p.text.strip()) > 50]  # Filter out short paragraphs
        
        # Extract headlines
        headlines = soup.find_all(['h1', 'h2', 'h3'])
        headlines = [h.text.strip() for h in headlines if len(h.text.strip()) > 0]
        
        # Extract lists
        lists = soup.find_all(['ul', 'ol'])
        lists = [' '.join([li.text.strip() for li in lst.find_all('li')]) for lst in lists]
        
        return {
            "content": content[:10],  # First 10 substantial paragraphs
            "headlines": headlines[:5],  # First 5 headlines
            "lists": lists[:3],  # Up to 3 lists
            "error": None
        }
    except Exception as e:
        logger.error(f"Error scraping website {url}: {str(e)}")
        return {"content": [], "headlines": [], "lists": [], "error": str(e)}

def get_search_results(query, num_results=3):
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
    try:
        html_content = fetch_data_with_selenium(search_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        search_results = soup.find_all('div', class_='yuRUbf')
        urls = [result.find('a')['href'] for result in search_results[:num_results]]
        return urls
    except Exception as e:
        logger.error(f"Error getting search results for query '{query}': {str(e)}")
        return []

def clear_results_file():
    os.makedirs("debug", exist_ok=True)
    with open('debug/results.txt', 'w') as f:
        f.write("")
    logger.info("Cleared results.txt file")

def search_and_scrape(topic, delete_results=True):
    logger.info(f"Starting search and scrape for topic: {topic}")
    
    if delete_results:
        clear_results_file()
    
    urls = get_search_results(topic, CONFIG["NUM_SEARCH_RESULTS"])
    
    if not urls:
        logger.warning(f"No search results found for topic: {topic}")
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG["NUM_SEARCH_RESULTS"]) as executor:
        future_to_url = {executor.submit(scrape_website, url): url for url in urls}
        results = []
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                results.append({"url": url, "data": data})
                
                with open('debug/results.txt', 'a') as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Headlines: {data['headlines']}\n")
                    f.write(f"Content snippets: {data['content']}\n")
                    f.write("---\n")
                
                logger.info(f"Successfully scraped data from {url}")
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
    
    return results

if __name__ == "__main__":
    # For testing purposes
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    test_topic = "Brazilian Central Bank latest data"
    results = search_and_scrape(test_topic)
    print(f"Found {len(results)} results for topic: {test_topic}")
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Headlines: {result['data']['headlines']}")
        print(f"Content snippets: {result['data']['content'][:2]}")  # First 2 content snippets
        print("---")