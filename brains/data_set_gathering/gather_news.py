import os
import csv
import requests
from goose3 import Goose
from datetime import datetime
from newsapi import NewsApiClient
from dataset_cleaner import clean_csv
import requests, sys
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
'''
Fetches articles about the given queries and saves them in the given filename as a csv file
'''

request_headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}

# White and backlist as specified in the Google Docs Drive
WHITELIST = 'marketwatch.com, fool.com, , economist.com, bloomberg.com, ft.com, reuters.com, investing.com, kiplinger.com, moneymorning.com'
BLACKLIST = 'kotaku.com, gizmodo.com, digitaltrends.com, stocknews.com, barrons.com'
NEWS_API_QUERY = ['Nvidia market', 'AMD market', 'Intel Market', 'ARM Holdings', 'TSMC Market', 'Semiconductor Market', 'Qualcomm', 'Micron Technologies'] 

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

def create_content_list(queries=NEWS_API_QUERY, domains=WHITELIST, excludeDomains=BLACKLIST) :
    content_list = []
    news_articles_list = []
    seen_urls = set() # To prevent duplicate articles
    goose = Goose()
    for news_query in queries:
        news_articles_list.append(api.get_everything(q=news_query, language='en', domains=domains, exclude_domains=excludeDomains, sort_by='relevancy'))
        content_list.append(scrape_yahoo_finance(news_query))
    index = 0
    for news_articles in news_articles_list:
        print(f"Getting article contents for '{queries[index]}'...")
        index += 1
        progress = 1
        for news in news_articles.get('articles'):
            url = news.get('url') # Checking the URL first can save time when building the dataset and reduce embedding calls
            if url in seen_urls:
                continue
            else:
                content_list.append(row_data(news, goose))
                seen_urls.add(url)
            print(f"Progress: [{progress}/{len(news_articles.get('articles'))}]", end="\r")
            progress += 1         
    return content_list


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

# now that we have urls, we can gather the info we want from each article
#  our search results contains 3 types of results:
# 1 - videos: videos contain "video" in the url, we can reject all videos
# 2 - redirects: redericts will take you to a portion of the article and have a link to the full article. 
#           We will scrape meta data from the yahoo finace page, scrape the real link, and use the real link to scrape the article content
# 3 - articles: the article is hosted directly on yahoo finance and no faurther work is needed
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

def make_yahoo_search_query(search_term):
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

def scrape_yahoo_finance(search_term):
    article_urls = make_yahoo_search_query(search_term)
    articles = explore_articles(article_urls)
    
    return articles


def main() :
    create_context_csv()
    
if __name__ == '__main__':
    main()