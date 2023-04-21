import os
import csv
import requests
from datetime import datetime
from time import sleep

# Gather and scrape articles from news api
from newsapi import NewsApiClient
from goose3 import Goose

# Selenium to explore search queries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Beutiful soup to explore collected articles
import requests
from bs4 import BeautifulSoup
from time import sleep

from dataset_cleaner import clean_csv

# When making a request, this is the infomation we pass to the website about our 
# request and our system
request_headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}

# White and backlist as specified in the Google Docs Drive
WHITELIST = 'marketwatch.com,fool.com,economist.com,bloomberg.com,ft.com,reuters.com,investing.com,kiplinger.com,moneymorning.com'
BLACKLIST = 'kotaku.com,gizmodo.com,digitaltrends.com,stocknews.com,barrons.com'

# Search tearms to be used by the news collection functions
NEWS_API_QUERY = ['Nvidia market', 'AMD market', 'Intel Market', 'ARM Holdings', 'TSMC Market', 'Semiconductor Market', 'Qualcomm', 'Micron Technologies'] 
YAHOO_FINANCE_QUERY = ['NVDA', 'AMD', 'INTC', 'TSMC34.SA', 'QCOM', 'MU']

# Required to get news articles from news api
api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

def create_context_csv():

    file_path = create_file_path('context')
    embed_file_path = create_file_path('embeds')
    
    if not os.path.exists(file_path):
        write_file(file_path, create_content_list())
        #after file is created, it is cleaned
        clean_csv(file_path, embed_file_path)
    else:
        print(f"The file {file_path} already exists. Skipping gathering articles.")

def create_file_path(file_type: str):
        today = datetime.today().strftime('%m-%d-%Y')
        directory = 'milvus_db\initial_data'
        file_name = f'{file_type}_{today}.csv'
        return os.path.join(directory, file_name)
    
def write_file(path, contents: list) :
    col_headers = ['URL','Title','Date','Content']
    print('Writing to file..')
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(col_headers)
        writer.writerows(contents)

SEEN_URLS = set() # To prevent duplicate articles

'''
Makes search queries to the news search functions
From the calls we make to news api and yahoo finance scraper, we will be returned content lists
'''
def gather_news():
    
    content_list = []
    
    for search_term in NEWS_API_QUERY:
        content_list += news_api_search_query(search_term)
    
    for search_term in YAHOO_FINANCE_QUERY:
        content_list += yahoo_finance_search_query(search_term)
    
    return content_list

'''
News api allows hundreds of articles on a given search term.
Using this api we may generate a content list of news articles for us to process later
'''
def news_api_search_query(search_term):
    content_list = []
    news_articles_list = []
    goose = Goose()
    for news_query in NEWS_API_QUERY:
        news_articles_list.append(api.get_everything(q=news_query, language='en', domains=WHITELIST, exclude_domains=BLACKLIST, sort_by='relevancy'))
    index = 0
    for news_articles in news_articles_list:
        print(f"Getting article contents for '{search_term}'...")
        index += 1
        progress = 1
        for news in news_articles.get('articles'):
            url = news.get('url') # Checking the URL first can save time when building the dataset and reduce embedding calls
            if url in SEEN_URLS:
                continue
            content_list.append(row_data(news, goose))
            SEEN_URLS.add(url)
            print(f"Progress: [{progress}/{len(news_articles.get('articles'))}]", end="\r")
            progress += 1         
    return content_list

'''
When we pull data from news api, the fromat the articles are delivered in are not what we want to work with
This function takes the data return from news api and formats s.t. we me process the data
'''
def row_data(n, g) :
    title = n.get('title')
    date = n.get('publishedAt')
    splitdate = date.split('T')
    ymd = splitdate[0] # ymd = year month day
    url = n.get('url')
    try :
        content = g.extract(url).cleaned_text
    except requests.exceptions.ReadTimeout:
        print('Goose Extraction Read Timeout')
    row_data = []
    row_data.append(url)
    row_data.append(title)
    row_data.append(ymd)
    row_data.append(content)
    return row_data

'''
News api does not allow to pull articles from within the last 24 hours
This function fills the gap left by news api
We use selenium to scroll a webpage and pull links from this webpage
'''
def yahoo_finance_search_query(search_term):
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
    # Sleep to allow time for page to fully load
    sleep(2)
    
    print(f"Begining Yahoo Finance Query for {search_term}")
    
    # Load search page
    screen_height = driver.execute_script("return window.screen.height;")
    scroll_amount = 5
    for i in range (scroll_amount):
        print(f"Progress: {i+1}/{scroll_amount}", end="\r")
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        sleep(1)
    print(f"Completed Yahoo Finance Query for {search_term}")
    print(f"Extrating links from {search_term} query")
    all_items=driver.find_elements(By.TAG_NAME,"a")
    
    links = []
    
    # Filter links to articles
    for item in all_items:
        link = item.get_attribute('href')
        if link in SEEN_URLS:
            continue
        if 'https://finance.yahoo.com/news/' in link or 'https://finance.yahoo.com/m/' in link:
            links.append(link)
            SEEN_URLS.add(link)
    print(f"Completed link extraction from {search_term} query")
    # We are done with our driver, we are now free to quit
    driver.quit()
    
    return links

'''
now that we have urls from our web scraper, we can gather the info we want from each article
Using these links we may generate a content list of news articles for us to process later
our search results contains 3 types of results:
1 - videos: videos contain "video" in the url, we can reject all videos
2 - redirects: redericts will take you to a portion of the article and have a link to the full article. 
        We will scrape meta data from the yahoo finace page, scrape the real link, and use the real link to scrape the article content
3 - articles: the article is hosted directly on yahoo finance and no further work is needed
'''
def explore_articles(article_urls):
    print("Extracting article content from links")
    articles = [['URL', 'Title', 'Date', 'Content']]
    for url in article_urls:
        print(f"Trying url '{url}'")
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
            print(f"Info from url '{url}' sucsessfully extracted")
        except Exception:
            print(f"Error extrating info from url '{url}' Error: {Exception}")
            articles.append(f"Error: {Exception}")
    print('Done extrating article content from urls')
    return articles

def create_content_list():
    print(gather_news)
    pass


if __name__ == '__main__':
    gather_news()
    #create_context_csv()
