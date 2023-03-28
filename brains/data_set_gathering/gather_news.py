import os
import csv
import requests
from goose3 import Goose
from datetime import datetime
from newsapi import NewsApiClient

'''
Fetches articles about the given company and saves them in the given filename as a csv file
'''

# White and backlist as specified in the Google Docs Drive
WHITELIST = 'marketwatch.com, fool.com, barrons.com, economist.com, bloomberg.com'
BLACKLIST = 'kotaku.com, gizmodo.com, digitaltrends.com, stocknews.com'
NEWS_API_QUERY = 'Nvidia market'

class NewsApiController:
    def __init__(self, api_key: str):
         self.api = NewsApiClient(api_key=api_key)
    
    def create_context_csv(self):
        today = datetime.today().strftime('%m-%d-%Y')
        directory = 'milvus_db\initial_data'
        file_name = f'context_{today}.csv'
        file_path = os.path.join(directory, file_name)
        contents =  self.create_content_list()
        print('Writing to file..')
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for content in contents:
                writer.writerow([content])
                
    def create_content_list(self, q=NEWS_API_QUERY, domains=WHITELIST, excludeDomains=BLACKLIST) :
        content_list = []
        content_list.append('context')
        news_articles = self.api.get_everything(q=q, language='en', domains=domains, exclude_domains=excludeDomains, sort_by='relevancy') # News Article is a nested dictionary
        g = Goose()
        print('Getting article contents..')
        for news in news_articles.get('articles'):
            try :
                title = news.get('title')
                date = news.get('publishedAt')
                url = news.get('url')
                content = g.extract(url=url).cleaned_text
            except requests.exceptions.ReadTimeout:
                print('News API Read Timeout')
            finally:
                row_data = f'{title}\n{date}\n{content}'
                content_list.append(row_data)
        return content_list