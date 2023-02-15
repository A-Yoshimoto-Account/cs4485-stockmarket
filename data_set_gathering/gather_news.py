import os
from dotenv import load_dotenv

import openpyxl
import pandas as pd
import requests
from goose3 import Goose

from newsapi import NewsApiClient

# Load API Keys from .env file
load_dotenv()

# Set News API Key
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

'''
Fetches articles about the given company and saves them in the given filename as a Microsoft Excel file
'''
def create_company_articles_workbook(company='Nvidia', filename='sample_fine_tune.xlsx'):
	# Create Python Goose Article Extractor Object
	g = Goose()

	# Create a workbook object
	workbook = openpyxl.Workbook()

	# Select the active sheet
	sheet = workbook.active

	# Perform call for get_everything endpoint of News API
	news_articles = newsapi.get_everything(q=company, language='en') # News Article is a nested dictionary

	# These column titles are necessary for putting the xlsx in a format recognizable by the OpenAI CLI data preparation tool
	sheet["A1"] = "Article Info"
	sheet["B1"] = "prompt"
	sheet["C1"] = "completion"

	row = 2 # began at the next row

	# extract the article text from each news article, if URL request timesout write information to xlsx
	for news in news_articles.get('articles'):
		try :
			url = news.get('url')
			article = g.extract(url=url)
			text = article.cleaned_text
			sheet.cell(row=row, column=1, value = 'Date Published: ' + news.get('publishedAt') + '\nTitle: ' + news.get('title') + '\nURL: ' + news.get('url'))
			sheet.cell(row=row, column=2, value = 'Date Published: ' + news.get('publishedAt') + '\nContent:\n\n' + text)
			row += 1
		except requests.exceptions.ReadTimeout:
			sheet.cell(row=row, column=1, value= '**URL TIMEOUT**, \n\n Date Published: ' + news.get('publishedAt') + '\nTitle: ' + news.get('title') + '\nURL: ' + news.get('url'))
			sheet.cell(row=row, column=2, value = 'Date Published: ' + news.get('publishedAt') + '\nTruncated Content: ' + news.get('content'))
			row += 1

	workbook.save(filename)
