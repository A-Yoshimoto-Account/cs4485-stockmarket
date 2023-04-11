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
    today = datetime.today().strftime('%m-%d-%Y')
    directory = 'milvus_db\initial_data'
    file_name = f'context_{today}.csv'
    embed_file_name = f'embeds_{today}.csv'
    file_path = os.path.join(directory, file_name)
    embed_file_path = os.path.join(directory, embed_file_name)
    
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

def create_content_list(queries=NEWS_API_QUERY, domains=WHITELIST, excludeDomains=BLACKLIST) :
    content_list = []
    news_articles_list = []
    seen_urls = set() # To prevent duplicate articles
    for news_query in queries:
        news_articles_list.append(api.get_everything(q=news_query, language='en', domains=domains, exclude_domains=excludeDomains, sort_by='relevancy')) # News Article is a nested dictionary
    g = Goose()
    count = 0
    for news_articles in news_articles_list:
        print(f"Getting article contents for '{queries[count]}'...")
        count += 1
        progress = 1
        for news in news_articles.get('articles'):
            try :
                url = news.get('url') # Checking the URL first can save time when building the dataset and reduce embedding calls
                if url in seen_urls:
                    continue
                else:
                    title = news.get('title')
                    date = news.get('publishedAt')
                    splitdate = date.split('T')
                    ymd = splitdate[0] # ymd = year month day
                    content = g.extract(url).cleaned_text
                    row_data = []
                    row_data.append(url)
                    row_data.append(title)
                    row_data.append(ymd)
                    row_data.append(content)
                    content_list.append(row_data)
                    seen_urls.add(url)
            except requests.exceptions.ReadTimeout:
                print('News API Read Timeout')
            finally:
                print(f"Progress: [{progress}/{len(news_articles.get('articles'))}]", end="\r")
                progress += 1         
    return content_list

def main() :
    create_context_csv()
    
if __name__ == '__main__':
    main()