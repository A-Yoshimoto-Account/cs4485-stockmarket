# 
import os
import csv
import requests
from goose3 import Goose
from datetime import datetime
from newsapi import NewsApiClient
from time import sleep

# Selenium to explore search queries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#from dataset_cleaner import clean_csv
# Information passed to the website about the client.
# We want are client to look normal
# White and backlist as specified in the Google Docs Drive
WHITELIST = 'marketwatch.com,fool.com,economist.com,bloomberg.com,ft.com,reuters.com,investing.com,kiplinger.com,moneymorning.com'
BLACKLIST = 'kotaku.com,gizmodo.com,digitaltrends.com,stocknews.com,barrons.com'

# Search tearms to be used by the news collection functions
NEWS_API_QUERY = ['Nvidia market', 'AMD market', 'Intel Market', 'ARM Holdings', 'TSMC Market', 'Semiconductor Market', 'Qualcomm', 'Micron Technologies'] 
YAHOO_FINANCE_QUERY = ['NVDA', 'AMD', 'INTC', 'TSMC34.SA', 'QCOM', 'MU']

api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

# Makes search queries to the news search functions
# From the calls we make to news api and yahoo finance scraper, we will be returned a list of links
# We will concatenate these links and return them to be explored else were
def gather_news_links():
    
    links = []
    
    for search_term in NEWS_API_QUERY:
        links += news_api_search_query(search_term)
    
    for search_term in YAHOO_FINANCE_QUERY:
        links += yahoo_finance_search_query(search_term)
    
    return links

# For a given search term, query news api for the links to relevant articles
def news_api_search_query(search_term):
    news_article_list = [api.get_everything(q=search_term, language='en', domains=WHITELIST, exclude_domains=BLACKLIST, sort_by='relevancy')]
    #news_article_list.append()

    links = []
    
    for news_article in news_article_list:
        for news in news_article['articles']:
            links.append(news.get('url'))
    return links

# For a given search term, query yahoo finance for the links to relevant articles 
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
        if 'https://finance.yahoo.com/news/' in link or 'https://finance.yahoo.com/m/' in link:
            links.append(link)
    print(f"Completed link extraction from {search_term} query")
    # We are done with our driver, we are now free to quit
    driver.quit()
    
    return links

if __name__ == '__main__':
    links = gather_news_links()
    print(links)
