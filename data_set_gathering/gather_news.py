import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
import openpyxl

# Load API Key
load_dotenv()

# Set News API Key
api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

# Create a workbook object
workbook = openpyxl.Workbook()

# Select the active sheet
sheet = workbook.active

# Perform REST call for get_everything endpoint of News API
news_articles = api.get_everything(q='ExxonMobil') # News Article is a nested dictionary

# These column titles are necessary for putting the xlsx in a format recognizable by the OpenAI CLI data preparation tool
sheet["A1"] = "prompt"
sheet["B1"] = "completion"

row = 2 # began at the next row
for news in news_articles.get('articles'):
    sheet.cell(row=row, column=1, value= news.get('content'))
    row += 1

workbook.save("sample_fine_tune.xlsx")