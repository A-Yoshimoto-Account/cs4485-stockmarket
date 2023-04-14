import os
import csv
import requests
from goose3 import Goose
from datetime import datetime
from newsapi import NewsApiClient
from dataset_cleaner import clean_csv

'''
Fetches articles about the given queries and saves them in the given filename as a csv file
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
        write_file(file_path, create_content_list())
        #after file is created, it is cleaned
        clean_csv(file_path, embed_file_path)
    else:
        print("This file already exists.")

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

def create_content_list(queries=NEWS_API_QUERY) :
    content_list = []
    seen_urls = set() # To prevent duplicate articles
    goose = Goose()
    index = 0
    for news_articles in create_article_list():
        print(f"Getting article contents for '{queries[index]}'...")
        index += 1
        progress = 1
        for news in news_articles.get('articles'):
            try :
                url = news.get('url') # Checking the URL first can save time when building the dataset and reduce embedding calls
                if url in seen_urls:
                    continue
                else:
                    content_list.append(row_data(news, goose))
                    seen_urls.add(url)
            except requests.exceptions.ReadTimeout:
                print('News API Read Timeout')
            finally:
                print(f"Progress: [{progress}/{len(news_articles.get('articles'))}]", end="\r")
                progress += 1         
    return content_list

def create_article_list(queries=NEWS_API_QUERY, domains=WHITELIST, excludeDomains=BLACKLIST) :
    na_list = []
    for news_query in queries:
        na_list.append(api.get_everything(q=news_query, language='en', domains=domains, exclude_domains=excludeDomains, sort_by='relevancy')) # News Article is a nested dictionary
    return na_list

def row_data(n, g) :
    title = n.get('title')
    date = n.get('publishedAt')
    splitdate = date.split('T')
    ymd = splitdate[0] # ymd = year month day
    url = n.get('url')
    content = g.extract(url).cleaned_text
    return create_row_data(url, title, ymd, content)

def create_row_data(u : str, t : str, y : str, c : str) :
    row_data = []
    row_data.append(u)
    row_data.append(t)
    row_data.append(y)
    row_data.append(c)
    return row_data

def main() :
    create_context_csv()
    
if __name__ == '__main__':
    main()