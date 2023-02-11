import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
import openpyxl
import requests
from goose3 import Goose

# Load API Key
load_dotenv()

# Set News API Key
api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

# Create Python Goose Article Extractor Object
g = Goose()

# Create a workbook object
workbook = openpyxl.Workbook()

# Select the active sheet
sheet = workbook.active

# Perform call for get_everything endpoint of News API
news_articles = api.get_everything(q='Nvidia', language='en') # News Article is a nested dictionary

# These column titles are necessary for putting the xlsx in a format recognizable by the OpenAI CLI data preparation tool
sheet["A1"] = "prompt"
sheet["B1"] = "completion"

row = 2 # began at the next row
for news in news_articles.get('articles'):
    try :
        url = news.get('url')
        article = g.extract(url=url)
        text = article.cleaned_text
        sheet.cell(row=row, column=1, value= 'Published: ' + news.get('publishedAt') + '\n Title: ' + news.get('title') + '\n URL: ' + news.get('url') + '\n Content: \n\n' + text)
        row += 1
    except requests.exceptions.ReadTimeout:
        sheet.cell(row=row, column=1, value= '**URL TIMEOUT**, \n\n Published: ' + news.get('publishedAt') + '\n Title: ' + news.get('title') + '\n URL: ' + news.get('url') + '\n Truncated Content: ' + news.get('content'))
        row += 1

workbook.save("sample_fine_tune.xlsx")