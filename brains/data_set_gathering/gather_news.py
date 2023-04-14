import os
import csv
import requests
from goose3 import Goose
from datetime import datetime
from newsapi import NewsApiClient
from dataset_cleaner import clean_csv

'''
Fetches articles about the given company and saves them in the given filename as a csv file
'''

# White and backlist as specified in the Google Docs Drive
WHITELIST = 'marketwatch.com, fool.com, , economist.com, bloomberg.com, ft.com, reuters.com, investing.com, kiplinger.com, moneymorning.com'
BLACKLIST = 'kotaku.com, gizmodo.com, digitaltrends.com, stocknews.com, barrons.com'
NEWS_API_QUERY = ['Nvidia market', 'AMD market', 'Intel Market', 'ARM Holdings', 'TSMC Market', 'Semiconductor Market', 'Qualcomm', 'Micron Technologies'] 

api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
    
def create_context_csv():

    file_path = create_file_path('context')
    embed_file_path = create_file_path('embeds')
    
    if not os.path.exists(file_path):
        col_headers = ['URL','Title','Date','Content']
        contents =  create_content_list()
        print('Writing to file..')
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(col_headers)
            writer.writerows(contents)

        #after file is created, it is cleaned
        clean_csv(file_path, embed_file_path)
    else:
        print("This file already exists.")
        #after file is created, it is cleaned
        clean_csv(file_path, embed_file_path)

def create_file_path(file_type: str):
        today = datetime.today().strftime('%m-%d-%Y')
        directory = 'milvus_db\initial_data'
        file_name = f'{file_type}_{today}.csv'
        return os.path.join(directory, file_name)
    
def create_content_list(queries=NEWS_API_QUERY, domains=WHITELIST, excludeDomains=BLACKLIST) :
    content_list = []
    news_articles_list = []
    seen_urls = set() # To prevent duplicate articles
    for news_query in queries:
        news_articles_list.append(api.get_everything(q=news_query, language='en', domains=domains, exclude_domains=excludeDomains, sort_by='relevancy')) # News Article is a nested dictionary
    index = 0
    for news_articles in news_articles_list:
        print(f"Getting article contents for '{queries[index]}'...")
        index += 1
        progress = 1
        for news in news_articles.get('articles'):
            try :
                url = news.get('url') # Checking the URL first can save time when building the dataset and reduce embedding calls
                if url in seen_urls:
                    continue
                else:
                    content_list.append(create_row_data(news))
                    seen_urls.add(url)
            except requests.exceptions.ReadTimeout:
                print('News API Read Timeout')
            finally:
                print(f"Progress: [{progress}/{len(news_articles.get('articles'))}]", end="\r")
                progress += 1         
    return content_list

def create_row_data(news_article) :
    g = Goose()
    title = news_article.get('title')
    date = news_article.get('publishedAt')
    splitdate = date.split('T')
    ymd = splitdate[0] # ymd = year month day
    url = news_article.get('url')
    content = g.extract(url).cleaned_text
    row_data = []
    row_data.append(url)
    row_data.append(title)
    row_data.append(ymd)
    row_data.append(content)
    return row_data

def main() :
    create_context_csv()
    
if __name__ == '__main__':
    main()