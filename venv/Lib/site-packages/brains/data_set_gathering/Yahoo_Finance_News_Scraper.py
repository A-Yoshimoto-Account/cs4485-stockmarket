import requests, sys, time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

# When a browser makes a request to a website, it passes basic info about the browser.
# With this header, we use this same interaction s.t. the scraper looks less like a bot
request_headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}

# From a yahoo finance search, we can pull urls to financial/buisness news on a search term search term
def make_search_query(search_term):
    url = f'https://finance.yahoo.com/quote/{search_term}?p={search_term}'
    
    # Make a request and parse the search page
    response = requests.get(url, request_headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    tags = soup.find_all('a', {'class': "js-content-viewer"})
    
    # Extract article links
    article_urls = []
    for refrence in tags:
        article_urls.append("https://finance.yahoo.com" + refrence['href']) 

    return article_urls

# now that we have urls, we can gather the info we want from each article
#  our search results contains 3 types of results:
# 1 - videos: videos contain "video" in the url, we can reject all videos
# 2 - redirects: redericts will take you to a portion of the article and have a link to the full article. 
#           We will scrape meta data from the yahoo finace page, scrape the real link, and use the real link to scrape the article content
# 3 - articles: the article is hosted directly on yahoo finance and no further work is needed
def explore_articles(article_urls):
    articles = []
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
                
            articles.append({'Title': title, 'Publish Date': publish_date, 'Source': url, 'Keywords':keywords, 'Content': content})
        except Exception:
            articles.append(f"Error: {Exception}")
        
    return articles

# Brings everything together
def scrape_yahoo_finance(search_term):
    article_urls = make_search_query(search_term)
    articles = explore_articles(article_urls)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    df = pd.DataFrame(articles)
    df.to_csv(f'results_{search_term}_{timestamp}.csv', index=False)