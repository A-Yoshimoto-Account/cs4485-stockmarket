import os
from dotenv import load_dotenv
import csv
import requests
from goose3 import Goose
from datetime import datetime
from newsapi import NewsApiClient
# Load API Keys from .env file
load_dotenv()

# Set News API Key
api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

'''
Fetches articles about the given company and saves them in the given filename as a csv file
'''

# White and backlist as specified in the Google Docs Drive
whitelist = 'marketwatch.com, fool.com, barrons.com, economist.com, bloomberg.com'
blacklist = 'kotaku.com, gizmodo.com, digitaltrends.com, stocknews.com'
news_api_query = 'Nvidia market'


def create_context_csv():
	# Current date for file name
	today = datetime.today().strftime('%m-%d-%Y')

	# Create file path directory to Milvus DB
	directory = 'milvus_db\initial_data'

	# create file name
	file_name = f'context_{today}.csv'

	# create full file path
	file_path = os.path.join(directory, file_name)
	
	contents =  create_content_list()
	
	with open(file_path, 'w', newline='') as file:
		writer = csv.writer(file)
		for content in contents:
				writer.writerow([content])

def create_content_list(q=news_api_query, domains=whitelist, excludeDomains=blacklist) :
# Create empty list to store article content
	content = []
# Perform call for get_everything endpoint of News API
	news_articles = newsapi.get_everything(q=q, language='en', domains=domains, exclude_domains=excludeDomains) # News Article is a nested dictionary
# Create Python Goose Article Extractor Object
	g = Goose()
# extract the article text from each news article
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
			content.append(row_data)
	return content