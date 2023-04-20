# Beutiful soup to explore collected articles
import requests
from bs4 import BeautifulSoup
from time import sleep

# Selenium to explore search queries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# When making a request, this is the infomation we pass to the website about our 
# request and our system
request_headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}

# now that we have urls, we can gather the info we want from each article
#  our search results contains 3 types of results:
# 1 - videos: videos contain "video" in the url, we can reject all videos
# 2 - redirects: redericts will take you to a portion of the article and have a link to the full article. 
#           We will scrape meta data from the yahoo finace page, scrape the real link, and use the real link to scrape the article content
# 3 - articles: the article is hosted directly on yahoo finance and no further work is needed
def explore_articles(article_urls):
    articles = [['URL', 'Title', 'Date', 'Content']]
    for url in article_urls:
        try:
            if "video" in url:
                continue

            response = requests.get(url, request_headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find_all('h1')[1].getText()
            publish_date = soup.find('time').get('datetime')
            keywords = soup.find('meta', attrs={'name': 'news_keywords'})['content']
            
            if "/m/" in url:
                tags = soup.find_all('a', {'class': "link caas-button"})
                url = tags[0]['href']
                response = requests.get(url, request_headers)
                soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            content = ''
            for paragraph in paragraphs:
                content += paragraph.get_text()
            
            splitdate = publish_date.split('T')
            ymd = splitdate[0] # ymd = year month day
              
            articles.append([url, title,  ymd, content])
        except Exception:
            articles.append(f"Error: {Exception}")
        
    return articles

def make_search_query(search_term):
    # Properly format search term into a valid yahoo finance url
    url = f'https://finance.yahoo.com/quote/{search_term}?p={search_term}'
    
    # Initialize webdriver components
    driver_install = ChromeDriverManager().install()
    service = Service(driver_install)
    options = Options()
    options.add_argument('--headless')
            
    # Build webdriver to allow search
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    
    # Load search page
    screen_height = driver.execute_script("return window.screen.height;")
    for i in range (5):
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        sleep(1)

    all_items=driver.find_elements(By.TAG_NAME,"a")
    
    links = []
    
    # Filter links to articles
    for item in all_items:
        link = item.get_attribute('href')
        if 'https://finance.yahoo.com/news/' in link or 'https://finance.yahoo.com/m/' in link:
            links.append(link)

    # We are done with our driver, we are now free to quit
    driver.quit()
    
    return links

# Helper method which makes a search, gathers article links, and gathers content from articles, returning a 2D array containing article contents
def scrape_yahoo_finance(search_term):
    article_urls = make_search_query(search_term)
    articles = explore_articles(article_urls)
    
    return articles




